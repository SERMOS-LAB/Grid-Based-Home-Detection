# ghost.cli: Command-line interface

import typer
from typing import Optional
from ghost.config import load_config, merge_config
from ghost.detector import HomeDetector
from ghost.plot import plot_full_result, plot_interactive_map
from ghost.validation.groundtruth import load_groundtruth_csv, compare_predictions_to_groundtruth
from ghost.validation.metrics import compute_accuracy_metrics
import pandas as pd
import sys
import os

app = typer.Typer(help="GHOST: Grid-based Home detection via Stay-Time (GHOST) CLI")

defaults = {
    'input_gpx': 'data.gpx',
    'output_csv': 'results.csv',
    'output_plot': 'results.png',
    'output_map': 'results.html',
    'grid_size': 20,
    'night_start': 22,
    'night_end': 6,
    'plot_basemap': False,
    'interactive_map': True,
    'groundtruth_csv': None
}

@app.command()
def detect(
    config: Optional[str] = typer.Option(None, help="Path to config file (YAML/JSON)"),
    input_gpx: Optional[str] = typer.Option(None, help="Input GPX file or folder or CSV"),
    output_csv: Optional[str] = typer.Option(None, help="Output CSV for results"),
    grid_size: Optional[int] = typer.Option(None, help="Grid size in meters"),
    night_start: Optional[int] = typer.Option(None, help="Night start hour (22=10pm)"),
    night_end: Optional[int] = typer.Option(None, help="Night end hour (6=6am)"),
):
    """
    Run the GHOST algorithm for home detection and save results. Uses the high-level HomeDetector workflow.
    """
    file_config = load_config(config) if config else {}
    cli_args = locals()
    config_all = merge_config(defaults, file_config, cli_args)
    # Set input_file in config for HomeDetector
    config_all['input_file'] = config_all.get('input_gpx')
    config_all['output_file'] = config_all.get('output_csv')
    detector = HomeDetector(config_all)
    detector.load_data().preprocess_data().detect_homes()
    results = detector.get_results()
    output_path = config_all['output_csv']
    results.to_csv(output_path, index=False)
    typer.echo(f"Saved results to {output_path}")
    user_id_col = config_all.get('user_id_column', 'user_id')
    if user_id_col in results.columns and results[user_id_col].nunique() > 1:
        typer.echo(f"Batch mode: processed {results[user_id_col].nunique()} users.")
        typer.echo(f"User IDs: {list(results[user_id_col])}")
        typer.echo("Each row in the CSV contains all stats for one user (lat, lon, stay_time, num_nights, inferred_from, etc.)")
    elif 'lat' in results.columns and 'lon' in results.columns:
        typer.echo(f"Home location:\n{results[[user_id_col,'lat','lon']]}")

@app.command()
def plot(
    config: Optional[str] = typer.Option(None, help="Path to config file (YAML/JSON)"),
    input_gpx: Optional[str] = typer.Option(None, help="Input GPX file or folder or CSV"),
    output_plot: Optional[str] = typer.Option(None, help="Output PNG for static plot"),
    output_map: Optional[str] = typer.Option(None, help="Output HTML for interactive map"),
    plot_basemap: Optional[bool] = typer.Option(None, help="Add OSM basemap (requires contextily)"),
    interactive_map: Optional[bool] = typer.Option(None, help="Create folium map"),
):
    """
    Plot GPS points and home location (static and/or interactive) using the GHOST algorithm.
    """
    file_config = load_config(config) if config else {}
    cli_args = locals()
    config_all = merge_config(defaults, file_config, cli_args)
    config_all['input_file'] = config_all.get('input_gpx')
    detector = HomeDetector(config_all)
    detector.load_data().preprocess_data().detect_homes()
    results = detector.get_results()
    user_id_col = config_all.get('user_id_column', 'user_id')
    # For batch: plot each user separately
    for _, row in results.iterrows():
        lat = row.get('lat')
        lon = row.get('lon')
        uid = row.get(user_id_col, 'user')
        # Static plot
        fig, ax = plot_full_result(detector.raw_data, lat, lon, basemap=config_all['plot_basemap'])
        fig.suptitle(f"Home Detection Result (User: {uid})")
        out_plot = config_all['output_plot']
        if results.shape[0] > 1:
            out_plot = out_plot.replace('.png', f'_{uid}.png')
        fig.savefig(out_plot, bbox_inches='tight')
        typer.echo(f"Saved static plot to {out_plot}")
        # Interactive map
        if config_all['interactive_map']:
            m = plot_interactive_map(detector.raw_data, lat, lon)
            if m is not None:
                out_map = config_all['output_map']
                if results.shape[0] > 1:
                    out_map = out_map.replace('.html', f'_{uid}.html')
                m.save(out_map)
                typer.echo(f"Saved interactive map to {out_map}")
            else:
                typer.echo("folium is not installed; skipping interactive map.")

@app.command()
def validate(
    config: Optional[str] = typer.Option(None, help="Path to config file (YAML/JSON)"),
    output_csv: Optional[str] = typer.Option(None, help="Predicted results CSV (from detect)"),
    groundtruth_csv: Optional[str] = typer.Option(None, help="Ground truth CSV"),
):
    """
    Compare GHOST-predicted home locations to ground truth and print accuracy metrics.
    """
    file_config = load_config(config) if config else {}
    cli_args = locals()
    config_all = merge_config(defaults, file_config, cli_args)
    if not config_all['groundtruth_csv']:
        typer.echo("No groundtruth_csv specified in config or CLI.")
        raise typer.Exit(1)
    pred_df = pd.read_csv(config_all['output_csv'])
    gt_df = load_groundtruth_csv(config_all['groundtruth_csv'])
    merged = compare_predictions_to_groundtruth(pred_df, gt_df)
    errors = merged['error_m'].values
    metrics = compute_accuracy_metrics(errors)
    user_id_col = 'user_id' if 'user_id' in merged.columns else merged.columns[0]
    if merged[user_id_col].nunique() > 1:
        typer.echo(f"Batch validation: {merged[user_id_col].nunique()} users compared.")
        typer.echo(f"User IDs: {list(merged[user_id_col])}")
        typer.echo("Per-user errors (meters):")
        for _, row in merged.iterrows():
            typer.echo(f"  {row[user_id_col]}: {row['error_m']:.2f} m")
        typer.echo("Summary accuracy metrics for batch:")
    else:
        typer.echo("Validation results for single user:")
    for k, v in metrics.items():
        typer.echo(f"{k}: {v}")
    typer.echo(f"Mean error: {metrics['mean_error']:.2f} m")
    typer.echo(f"Median error: {metrics['median_error']:.2f} m")
    for t in [50, 100, 200]:
        key = f'percent_within_{t}m'
        if key in metrics:
            typer.echo(f"% within {t}m: {metrics[key]:.1f}%")

if __name__ == "__main__":
    app() 
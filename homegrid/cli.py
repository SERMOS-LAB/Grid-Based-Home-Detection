# homegrid.cli: Command-line interface

import typer
from typing import Optional
from homegrid.config import load_config, merge_config
from homegrid.io.gpx import read_gpx
from homegrid.algorithms.grid import GridHomeDetector
from homegrid.plot import plot_full_result, plot_interactive_map
from homegrid.validation.groundtruth import load_groundtruth_csv, compare_predictions_to_groundtruth
from homegrid.validation.metrics import compute_accuracy_metrics
import pandas as pd
import sys
import os

app = typer.Typer(help="Grid-Based Home Detection CLI")

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
    input_gpx: Optional[str] = typer.Option(None, help="Input GPX file"),
    output_csv: Optional[str] = typer.Option(None, help="Output CSV for results"),
    grid_size: Optional[int] = typer.Option(None, help="Grid size in meters"),
    night_start: Optional[int] = typer.Option(None, help="Night start hour (22=10pm)"),
    night_end: Optional[int] = typer.Option(None, help="Night end hour (6=6am)"),
):
    """
    Run grid-based home detection and save results.
    """
    file_config = load_config(config) if config else {}
    cli_args = locals()
    config_all = merge_config(defaults, file_config, cli_args)
    df = read_gpx(config_all['input_gpx'])
    detector = GridHomeDetector(
        grid_size=config_all['grid_size'],
        night_start=config_all['night_start'],
        night_end=config_all['night_end']
    )
    home_lat, home_lon, stats = detector.fit(df)
    results = pd.DataFrame([{
        'user_id': 1,  # single user for now
        'lat': home_lat,
        'lon': home_lon,
        **stats
    }])
    results.to_csv(config_all['output_csv'], index=False)
    typer.echo(f"Saved results to {config_all['output_csv']}")
    typer.echo(f"Home location: {home_lat}, {home_lon}")

@app.command()
def plot(
    config: Optional[str] = typer.Option(None, help="Path to config file (YAML/JSON)"),
    input_gpx: Optional[str] = typer.Option(None, help="Input GPX file"),
    output_plot: Optional[str] = typer.Option(None, help="Output PNG for static plot"),
    output_map: Optional[str] = typer.Option(None, help="Output HTML for interactive map"),
    plot_basemap: Optional[bool] = typer.Option(None, help="Add OSM basemap (requires contextily)"),
    interactive_map: Optional[bool] = typer.Option(None, help="Create folium map"),
):
    """
    Plot GPS points and home location (static and/or interactive).
    """
    file_config = load_config(config) if config else {}
    cli_args = locals()
    config_all = merge_config(defaults, file_config, cli_args)
    df = read_gpx(config_all['input_gpx'])
    detector = GridHomeDetector(
        grid_size=config_all['grid_size'],
        night_start=config_all['night_start'],
        night_end=config_all['night_end']
    )
    home_lat, home_lon, stats = detector.fit(df)
    # Static plot
    fig, ax = plot_full_result(df, home_lat, home_lon, basemap=config_all['plot_basemap'])
    fig.suptitle("Home Detection Result (Static)")
    fig.savefig(config_all['output_plot'], bbox_inches='tight')
    typer.echo(f"Saved static plot to {config_all['output_plot']}")
    # Interactive map
    if config_all['interactive_map']:
        m = plot_interactive_map(df, home_lat, home_lon)
        if m is not None:
            m.save(config_all['output_map'])
            typer.echo(f"Saved interactive map to {config_all['output_map']}")
        else:
            typer.echo("folium is not installed; skipping interactive map.")

@app.command()
def validate(
    config: Optional[str] = typer.Option(None, help="Path to config file (YAML/JSON)"),
    output_csv: Optional[str] = typer.Option(None, help="Predicted results CSV (from detect)"),
    groundtruth_csv: Optional[str] = typer.Option(None, help="Ground truth CSV"),
):
    """
    Compare predicted home locations to ground truth and print accuracy metrics.
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
    typer.echo("Validation results:")
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
# GHOST Examples

This directory contains minimal, focused example scripts for using the GHOST package for home location detection from GPS data.

## Example Scripts

- **example_detect_single.py**: Run single-user detection on a single GPX file. Prints the result.
- **example_detect_batch.py**: Run batch detection on a folder of GPX files (one per user) or a CSV with multiple users. Prints the results.
- **example_plot_single.py**: Plot static and interactive maps for a single user after detection.
- **example_plot_batch.py**: Generate static and interactive plots for all users in a batch using `plot_batch_results`.
- **example_validate_single.py**: Validate single-user detection results against ground truth using `batch_validation_report`.
- **example_validate_batch.py**: Validate batch detection results against ground truth using `batch_validation_report`. Prints per-user errors and batch summary.

## Usage

Run any script with:

```
python examples/<script_name.py>
```

Make sure you have the required input files (e.g., `data.gpx`, `data_folder/`, `data_multiuser.csv`, `groundtruth.csv`) in the project root or update the script paths accordingly.

See the main project README for more details and API documentation. 
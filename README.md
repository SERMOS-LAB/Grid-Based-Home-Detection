# Grid-Based Home Detection

This project is an open-source, modular Python package for detecting home locations from mobile GPS data, with a focus on grid-based algorithms. It supports both single-user and batch processing, robust validation, and reproducible workflows.

## Input Data Requirements

- Input can be a single GPX file, a folder of GPX files (one per user), or a CSV with multiple users.
- All input data must have the following columns and types:
  - `timestamp` (datetime, e.g., `2024-07-01T23:00:00`)
  - `lat` (float)
  - `lon` (float)
  - `user_id` (string/int, required for batch CSV; for GPX folders, inferred from filename)
- All internal processing uses GeoPandas GeoDataFrames for robust geospatial operations.

## Usage Overview

- **Detection, plotting, and validation workflows** (including batch and single-user modes) are all demonstrated in the `examples/` directory. See the example scripts for end-to-end usage.
- The CLI and Python API both support flexible configuration and batch processing.

## Command-Line Interface (CLI)

Run the full pipeline from the command line using the Typer-based CLI:

```
python -m homegrid.cli detect --config examples/config.yaml
python -m homegrid.cli plot --config examples/config.yaml
python -m homegrid.cli validate --output-csv results.csv --groundtruth-csv groundtruth.csv
```

Or override any parameter via CLI:
```
python -m homegrid.cli detect --input-gpx data.gpx --grid-size 30
python -m homegrid.cli detect --input-gpx data_folder/ --user-id-column user_id
```

## Configuration

- All parameters can be set in a YAML or JSON config file (see `examples/config.yaml`).
- Any parameter can be overridden via CLI flags.
- Example config file:

```yaml
input_file: data_folder/         # Can be a GPX file, folder, or CSV
output_file: results.csv
user_id_column: user_id         # Column for user IDs (for batch CSV)
grid_size: 20                   # meters
night_start: 22                 # hour (22 = 10pm)
night_end: 6                    # hour (6 = 6am)
output_plot: results.png
output_map: results.html
plot_basemap: false             # true to add OSM basemap (requires contextily)
interactive_map: true           # true to create folium map
groundtruth_csv: groundtruth.csv
```

## Library Usage

Use the package as a library in Python scripts or notebooks:

```python
from homegrid.detector import HomeDetector

detector = HomeDetector.from_config_file('examples/config.yaml')
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
print(results)
```

## Notes
- All workflows (detection, plotting, validation, batch/single-user) are demonstrated in the `examples/` directory.
- All internal processing uses GeoDataFrames (via GeoPandas).
- Config keys: use `input_file`, `output_file`, and `user_id_column` for new workflows.

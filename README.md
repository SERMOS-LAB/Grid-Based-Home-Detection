# GHOST: Grid-based Home detection via Stay-Time

This project is an open-source, modular Python package for detecting home locations from mobile GPS data, branded as **GHOST** (Grid-based Home detection via Stay-Time). It supports both single-user and batch processing, robust validation, and reproducible workflows.

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
- The CLI and Python API both support flexible configuration and batch processing using the GHOST algorithm.

## Batch Processing

This package supports batch processing for multiple users using the GHOST algorithm:
- **Input:** A folder of GPX files (one per user, filename = user ID) or a CSV file with a `user_id` column.
- **Output:** A DataFrame or CSV with one row per user, including their inferred home location and all stats (e.g., stay_time, num_nights, inferred_from).
- **Automatic:** Batch mode is triggered automatically if your input contains multiple users.

## Command-Line Interface (CLI)

Run the full pipeline from the command line using the Typer-based CLI for GHOST:

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

**Batch Output:**
- When running in batch mode, the CLI will output a CSV with one row per user, including all stats (e.g., user_id, lat, lon, stay_time, num_nights, inferred_from).
- The CLI output will indicate batch mode and display user IDs.

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

Use the GHOST package as a library in Python scripts or notebooks:

```python
from homegrid.detector import HomeDetector

# For a folder of GPX files (batch mode)
detector = HomeDetector(input_file='data_folder/')
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
print(results)
```

- If your input is a folder of GPX files or a CSV with a `user_id` column, batch processing is triggered automatically.
- The output DataFrame will have one row per user with all stats.

## Notes
- All workflows (detection, plotting, validation, batch/single-user) are demonstrated in the `examples/` directory.
- All internal processing uses GeoDataFrames (via GeoPandas).
- Config keys: use `input_file`, `output_file`, and `user_id_column` for new workflows.
- The GHOST algorithm is validated against ground-truth data and compared to DBSCAN and KMeans++ in the accompanying manuscript.

## How to Cite

If you use GHOST in your research, please cite:

```bibtex
@misc{recalde2025ghost,
  author = {Alessandra Recalde and Mustafa Sameen and Xiaojian Zhang and Xilei Zhao},
  title = {DESIGN AND VALIDATION OF A GRID-BASED HOME DETECTION VIA STAY-TIME (GHOST) SOFTWARE FOR MOBILE LOCATION DATA},
  year = {2025},
  note = {University of Florida},
  howpublished = {\url{https://github.com/SERMOS-LAB/Grid-Based-Home-Detection}},
  institution = {University of Florida},
  address = {Gainesville, Florida, 32611}
}
```

---

For full API documentation and examples, see the `docs/` directory.

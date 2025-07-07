# Grid-Based Home Detection

This project is an open-source, modular Python package for detecting home locations from mobile GPS data, with a focus on grid-based algorithms.

## Input Data Requirements

- The current GPX parser is tailored to a specific format (tested with Gravy data) and may not work with all GPX files.
- Input data (GPX or DataFrame) **must** have the following columns and types:
  - `timestamp` (datetime, e.g., `2024-07-01T23:00:00`)
  - `lat` (float)
  - `lon` (float)

## Command-Line Interface (CLI)

You can run the full pipeline from the command line using the Typer-based CLI:

### Detect home location
```
python -m homegrid.cli detect --config examples/config.yaml
```
Or override any parameter via CLI:
```
python -m homegrid.cli detect --input-gpx data.gpx --grid-size 30
```

### Plot results
```
python -m homegrid.cli plot --config examples/config.yaml
```

### Validate against ground truth
```
python -m homegrid.cli validate --config examples/config.yaml
```

---

## Configuration Management

- All parameters can be set in a YAML or JSON config file (see `examples/config.yaml`).
- Any parameter can be overridden via CLI flags.
- Example config file:

```yaml
input_gpx: data.gpx
output_csv: results.csv
grid_size: 20
night_start: 22
night_end: 6
plot_basemap: false
interactive_map: true
groundtruth_csv: groundtruth.csv
```

---

## Library Usage

You can also use the package as a library in Python scripts or notebooks:

```python
from homegrid.io.gpx import read_gpx
from homegrid.algorithms.grid import GridHomeDetector

df = read_gpx("data.gpx")
detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
home_lat, home_lon, stats = detector.fit(df)
print(home_lat, home_lon, stats)
```

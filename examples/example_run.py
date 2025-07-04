"""
Example: Run grid-based home detection on data.gpx

Usage:
    python examples/example_run.py

Make sure you have installed all dependencies (see pyproject.toml) and that data.gpx is present in the project root.
"""
from homegrid.io.gpx import read_gpx
from homegrid.algorithms.grid import GridHomeDetector

# 1. Parse GPX file
df = read_gpx("data.gpx")

# 2. Run grid-based home detection
detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
home_lat, home_lon, stats = detector.fit(df)

print("Inferred home location:")
print("Latitude:", home_lat)
print("Longitude:", home_lon)
print("Stats:", stats) 
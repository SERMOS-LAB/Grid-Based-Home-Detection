"""
Example: Visualize home detection results on a map (static and interactive)

Usage:
    python examples/example_plot.py

Requires: matplotlib, folium, contextily (optional for basemap)
"""
from homegrid.io.gpx import read_gpx
from homegrid.algorithms.grid import GridHomeDetector
from homegrid.plot import plot_full_result, plot_interactive_map
import matplotlib.pyplot as plt

# 1. Parse GPX file
df = read_gpx("data.gpx")

# 2. Run grid-based home detection
detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
home_lat, home_lon, stats = detector.fit(df)

# 3. Static plot (matplotlib)
fig, ax = plot_full_result(df, home_lat, home_lon, basemap=False)
plt.title("Home Detection Result (Static)")
plt.savefig("examples/home_detection_result.png", bbox_inches='tight')
print("Saved static plot to examples/home_detection_result.png")

# 4. Interactive map (folium)
map_obj = plot_interactive_map(df, home_lat, home_lon)
if map_obj is not None:
    map_obj.save("examples/home_detection_result.html")
    print("Saved interactive map to examples/home_detection_result.html")
else:
    print("folium is not installed; skipping interactive map.") 
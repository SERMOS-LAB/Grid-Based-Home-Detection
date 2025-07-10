"""
Example: Visualize home detection results on a map (static and interactive)

Usage:
    python examples/example_plot.py

Requires: matplotlib, folium, contextily (optional for basemap)
"""
from homegrid.detector import HomeDetector
from homegrid.plot import plot_full_result, plot_interactive_map
import matplotlib.pyplot as plt

# 1. Run detection using HomeDetector with direct parameters
print("--- HomeDetector with direct parameters for plotting ---")
detector = HomeDetector(input_file='data.gpx', grid_size=20, night_start=22, night_end=6)
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
input_gdf = detector.preprocessed_data
user_id_col = detector.config.get('user_id_column', 'user_id')

# 2. Plot for each user (batch or single)
for _, row in results.iterrows():
    user_id = row[user_id_col]
    home_lat = row['lat']
    home_lon = row['lon']
    user_points = input_gdf[input_gdf[user_id_col] == user_id]
    # Static plot
    fig, ax = plot_full_result(user_points, home_lat, home_lon, basemap=False)
    plt.title(f"Home Detection Result (User: {user_id})")
    out_png = f"examples/home_detection_result_{user_id}.png"
    fig.savefig(out_png, bbox_inches='tight')
    print(f"Saved static plot to {out_png}")
    # Interactive map
    map_obj = plot_interactive_map(user_points, home_lat, home_lon)
    if map_obj is not None:
        out_html = f"examples/home_detection_result_{user_id}.html"
        map_obj.save(out_html)
        print(f"Saved interactive map to {out_html}")
    else:
        print("folium is not installed; skipping interactive map.")
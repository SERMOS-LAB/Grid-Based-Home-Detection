"""
Minimal Example: Single-user plotting with GHOST

Usage:
    python examples/example_plot_single.py
"""
from ghost.detector import HomeDetector
from ghost.plot import plot_full_result, plot_interactive_map
import matplotlib.pyplot as plt

detector = HomeDetector(input_file='data.gpx')
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
row = results.iloc[0]
fig, ax = plot_full_result(detector.raw_data, row['lat'], row['lon'])
plt.title("GHOST Home Detection (Single User)")
fig.savefig("ghost_plot_single.png", bbox_inches='tight')
print("Saved static plot to ghost_plot_single.png")
m = plot_interactive_map(detector.raw_data, row['lat'], row['lon'])
m.save("ghost_map_single.html")
print("Saved interactive map to ghost_map_single.html") 
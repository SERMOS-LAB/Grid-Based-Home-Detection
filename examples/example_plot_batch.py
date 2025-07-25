"""
Minimal Example: Batch plotting with GHOST

Usage:
    python examples/example_plot_batch.py
"""
from ghost.detector import HomeDetector
from ghost.plot import plot_batch_results

input_path = 'data_folder/'  # or 'data_multiuser.csv'
detector = HomeDetector(input_file=input_path)
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
plot_batch_results(results, detector.raw_data)
print("Batch plots saved for all users.") 
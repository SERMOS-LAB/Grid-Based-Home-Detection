"""
Example: Run grid-based home detection (single-user or batch) using HomeDetector

Usage:
    python examples/example_run.py

Make sure you have installed all dependencies (see pyproject.toml) and that your input file (data.gpx, data_folder/, or data.csv) is present in the project root.
"""
from ghost.detector import HomeDetector

# 1. Using defaults (will not run unless you set input_file in config)
print("--- HomeDetector with defaults (will fail unless input_file is set) ---")
try:
    detector = HomeDetector()
    print("Config:", detector.config)
    # detector.load_data().preprocess_data().detect_homes()
    # results = detector.get_results()
    # print(results)
except Exception as e:
    print("(Expected error if input_file is not set):", e)

# 2. Using a config dictionary
print("\n--- HomeDetector with config dict ---")
my_config = {'input_file': 'data.gpx', 'grid_size': 20, 'night_start': 22, 'night_end': 6}
detector = HomeDetector(config=my_config)
print("Config:", detector.config)
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
print("Results:")
print(results)

# 3. Using direct parameters (kwargs)
print("\n--- HomeDetector with direct parameters ---")
detector = HomeDetector(input_file='data.gpx', grid_size=30, night_start=21, night_end=7)
print("Config:", detector.config)
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
print("Results:")
print(results)

# 4. Mixing config and kwargs (kwargs win)
print("\n--- HomeDetector with config dict and kwargs (kwargs win) ---")
detector = HomeDetector(config=my_config, grid_size=100)
print("Config:", detector.config)
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
print("Results:")
print(results)
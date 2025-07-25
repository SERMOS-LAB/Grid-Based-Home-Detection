"""
Minimal Example: Single-user detection with GHOST

Usage:
    python examples/example_detect_single.py
"""
from ghost.detector import HomeDetector

detector = HomeDetector(input_file='data.gpx')
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
print("Single-user detection result:")
print(results) 
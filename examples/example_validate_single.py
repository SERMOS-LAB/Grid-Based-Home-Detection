"""
Minimal Example: Single-user validation with GHOST

Usage:
    python examples/example_validate_single.py
"""
from ghost.detector import HomeDetector
from ghost.validation.groundtruth import batch_validation_report

detector = HomeDetector(input_file='data.gpx')
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
merged, metrics = batch_validation_report(results, 'groundtruth.csv') 
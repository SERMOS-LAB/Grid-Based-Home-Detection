"""
Minimal Example: Batch validation with GHOST

Usage:
    python examples/example_validate_batch.py
"""
from ghost.detector import HomeDetector
from ghost.validation.groundtruth import batch_validation_report

input_path = 'data_folder/'  # or 'data_multiuser.csv'
detector = HomeDetector(input_file=input_path)
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
merged, metrics = batch_validation_report(results, 'groundtruth.csv') 
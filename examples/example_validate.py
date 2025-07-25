"""
Example: Validate home detection results against ground truth

Usage:
    python examples/example_validate.py

This script runs home detection on data.gpx, compares the result to groundtruth.csv,
and prints validation metrics (mean error, % within 50m, etc).
"""
from ghost.detector import HomeDetector
from ghost.validation.groundtruth import load_groundtruth_csv, compare_predictions_to_groundtruth
from ghost.validation.metrics import compute_accuracy_metrics
import pandas as pd

# Validate using direct parameters only
print("\n--- Validation with direct parameters ---")
detector = HomeDetector(input_file='data.gpx', grid_size=20, night_start=22, night_end=6)
print("Config:", detector.config)
detector.load_data().preprocess_data().detect_homes()
pred_df = detector.get_results()
print("Predicted home locations:")
print(pred_df)
gt_df = load_groundtruth_csv('groundtruth.csv')
merged = compare_predictions_to_groundtruth(pred_df, gt_df)
print("\nValidation metrics:")
errors = merged['error_m'].values
metrics = compute_accuracy_metrics(errors)
for k, v in metrics.items():
    print(f"{k}: {v}")
if 'mean_error' in metrics:
    print(f"Mean error: {metrics['mean_error']:.2f} m")
if 'median_error' in metrics:
    print(f"Median error: {metrics['median_error']:.2f} m")
for t in [50, 100, 200]:
    key = f'percent_within_{t}m'
    if key in metrics:
        print(f"% within {t}m: {metrics[key]:.1f}%") 
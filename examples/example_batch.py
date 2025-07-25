"""
Example: Batch processing for home detection

Usage:
    python examples/example_batch.py

This script demonstrates how to run home detection in batch mode on a folder of GPX files (one per user)
or a CSV file with multiple users. It prints the results and saves them to a CSV file.
"""
from ghost.detector import HomeDetector
import pandas as pd

# Example: batch processing from a folder of GPX files
print("\n--- Batch processing from folder of GPX files ---")
detector = HomeDetector(input_file='data_folder/', grid_size=20, night_start=22, night_end=6)
print("Config:", detector.config)
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
print("Batch results:")
print(results)
results.to_csv('batch_results.csv', index=False)
print("Results saved to batch_results.csv")

# Example: batch processing from a CSV with multiple users
# Uncomment and edit the path if you have a suitable CSV
# print("\n--- Batch processing from CSV with multiple users ---")
# detector = HomeDetector(input_file='data_multiuser.csv', grid_size=20, night_start=22, night_end=6)
# detector.load_data().preprocess_data().detect_homes()
# results = detector.get_results()
# print("Batch results:")
# print(results)
# results.to_csv('batch_results_from_csv.csv', index=False)
# print("Results saved to batch_results_from_csv.csv") 
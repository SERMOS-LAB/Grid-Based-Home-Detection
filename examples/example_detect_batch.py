"""
Minimal Example: Batch detection with GHOST

Usage:
    python examples/example_detect_batch.py
"""
from ghost.detector import HomeDetector

# Use a folder of GPX files (one per user) or a CSV with user_id column
input_path = 'data_folder/'  # or 'data_multiuser.csv'
detector = HomeDetector(input_file=input_path)
detector.load_data().preprocess_data().detect_homes()
results = detector.get_results()
print("Batch detection results:")
print(results) 
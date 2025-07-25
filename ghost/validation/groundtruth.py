import pandas as pd
import numpy as np
from typing import Dict, Any
from ghost.validation.metrics import haversine_distance, compute_accuracy_metrics

def load_groundtruth(filepath: str) -> pd.DataFrame:
    """
    Load ground-truth home locations from a CSV or similar file.
    Returns DataFrame with columns ['user_id', 'lat', 'lon', ...]
    """
    # Implementation to be added
    raise NotImplementedError("Ground-truth loading not yet implemented.")

def load_groundtruth_csv(filepath: str) -> pd.DataFrame:
    """
    Load ground-truth home locations from a CSV file.
    Args:
        filepath: Path to CSV file (columns: user_id, lat, lon, ...)
    Returns:
        DataFrame with columns ['user_id', 'lat', 'lon', ...]
    Example:
        >>> df = load_groundtruth_csv('groundtruth.csv')
        >>> print(df.head())
    """
    df = pd.read_csv(filepath)
    required = {'user_id', 'lat', 'lon'}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required}")
    return df


def compare_predictions_to_groundtruth(pred_df: pd.DataFrame, gt_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare predicted home locations to ground truth and compute error metrics.
    Args:
        pred_df: DataFrame with columns ['user_id', 'lat', 'lon']
        gt_df: DataFrame with columns ['user_id', 'lat', 'lon']
    Returns:
        DataFrame with columns ['user_id', 'pred_lat', 'pred_lon', 'gt_lat', 'gt_lon', 'error_m']
    Example:
        >>> pred = pd.DataFrame({'user_id': [1], 'lat': [38.9], 'lon': [-104.8]})
        >>> gt = pd.DataFrame({'user_id': [1], 'lat': [38.9001], 'lon': [-104.8001]})
        >>> df = compare_predictions_to_groundtruth(pred, gt)
        >>> print(df)
    """
    merged = pd.merge(pred_df, gt_df, on='user_id', suffixes=('_pred', '_gt'))
    merged['error_m'] = haversine_distance(
        merged['lat_pred'], merged['lon_pred'], merged['lat_gt'], merged['lon_gt']
    )
    return merged[['user_id', 'lat_pred', 'lon_pred', 'lat_gt', 'lon_gt', 'error_m']]

def batch_validation_report(results, groundtruth_csv, user_id_col='user_id'):
    """
    Compare batch results to ground truth, print per-user errors and batch summary.

    Args:
        results (pd.DataFrame): Batch results DataFrame (one row per user).
        groundtruth_csv (str): Path to ground truth CSV.
        user_id_col (str): User ID column name.
    Returns:
        merged (pd.DataFrame): DataFrame with per-user errors.
        metrics (dict): Batch summary metrics.
    """
    gt_df = load_groundtruth_csv(groundtruth_csv)
    merged = compare_predictions_to_groundtruth(results, gt_df)
    if user_id_col in merged.columns and merged[user_id_col].nunique() > 1:
        print(f"Batch validation: {merged[user_id_col].nunique()} users compared.")
        print(f"User IDs: {list(merged[user_id_col])}")
        print("Per-user errors (meters):")
        for _, row in merged.iterrows():
            print(f"  {row[user_id_col]}: {row['error_m']:.2f} m")
        print("Summary accuracy metrics for batch:")
    else:
        print("Validation results for single user:")
    from .metrics import compute_accuracy_metrics
    errors = merged['error_m'].values
    metrics = compute_accuracy_metrics(errors)
    print(metrics)
    return merged, metrics 
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
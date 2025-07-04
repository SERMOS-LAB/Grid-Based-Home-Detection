import numpy as np
import pandas as pd
from typing import Tuple, List, Dict


def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    """
    Compute the great-circle (haversine) distance in meters between two points.
    Args:
        lat1, lon1: Latitude and longitude of point 1 (float or array-like, degrees)
        lat2, lon2: Latitude and longitude of point 2 (float or array-like, degrees)
    Returns:
        Distance in meters (float or np.ndarray)
    Example:
        >>> d = haversine_distance(38.9, -104.8, 38.9001, -104.8001)
        >>> print(round(d, 2))
    """
    R = 6371000  # Earth radius in meters
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


def compute_accuracy_metrics(errors: np.ndarray, thresholds: List[float] = [50, 100, 200]) -> Dict[str, float]:
    """
    Compute accuracy metrics for home detection errors.
    Args:
        errors: Array of error distances (meters)
        thresholds: List of thresholds (meters) for percent within X meters
    Returns:
        Dictionary with mean, median, and percent within each threshold
    Example:
        >>> errors = np.array([10, 50, 120, 300])
        >>> metrics = compute_accuracy_metrics(errors)
        >>> print(metrics)
    """
    metrics = {
        'mean_error': float(np.mean(errors)),
        'median_error': float(np.median(errors)),
    }
    for t in thresholds:
        metrics[f'percent_within_{t}m'] = float(np.mean(errors <= t)) * 100
    return metrics 
import numpy as np
from ghost.validation.metrics import haversine_distance, compute_accuracy_metrics

def test_haversine_distance_basic():
    d = haversine_distance(38.9, -104.8, 38.9001, -104.8001)
    assert 0 < d < 20  # Should be a small distance in meters
    # Test array input
    d_arr = haversine_distance([38.9, 38.9], [-104.8, -104.8], [38.9001, 38.9002], [-104.8001, -104.8002])
    assert isinstance(d_arr, np.ndarray)
    assert d_arr.shape == (2,)

def test_compute_accuracy_metrics():
    errors = np.array([10, 50, 120, 300])
    metrics = compute_accuracy_metrics(errors, thresholds=[50, 100, 200])
    assert np.isclose(metrics['mean_error'], 120)
    assert np.isclose(metrics['median_error'], 85)
    assert np.isclose(metrics['percent_within_50m'], 50.0)
    assert np.isclose(metrics['percent_within_100m'], 50.0)
    assert np.isclose(metrics['percent_within_200m'], 75.0) 
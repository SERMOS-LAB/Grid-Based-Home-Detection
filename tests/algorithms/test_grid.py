import pandas as pd
import numpy as np
from homegrid.algorithms.grid import GridHomeDetector

def test_grid_home_detector_basic():
    df = pd.DataFrame({
        'lat': [38.9, 38.9, 38.9001],
        'lon': [-104.8, -104.8, -104.8001],
        'timestamp': ['2024-07-01T23:30:00', '2024-07-02T01:00:00', '2024-07-02T02:00:00']
    })
    detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
    home_lat, home_lon, stats = detector.fit(df)
    assert not np.isnan(home_lat)
    assert not np.isnan(home_lon)
    assert stats['num_nights'] >= 1
    assert stats['num_points'] >= 1

def test_grid_home_detector_empty():
    df = pd.DataFrame({'lat': [], 'lon': [], 'timestamp': []})
    detector = GridHomeDetector()
    home_lat, home_lon, stats = detector.fit(df)
    assert np.isnan(home_lat)
    assert np.isnan(home_lon)
    assert stats['num_nights'] == 0
    assert stats['num_points'] == 0 
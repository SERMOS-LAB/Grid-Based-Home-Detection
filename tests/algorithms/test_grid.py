import pandas as pd
import numpy as np
from homegrid.algorithms.grid import GridHomeDetector, grid_based_batch
import geopandas as gpd

def test_grid_home_detector_basic():
    df = pd.DataFrame({
        'lat': [38.9, 38.9, 38.9001],
        'lon': [-104.8, -104.8, -104.8001],
        'timestamp': ['2024-07-01T23:30:00', '2024-07-02T01:00:00', '2024-07-02T02:00:00']
    })
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
    home_lat, home_lon, stats = detector.fit(df)
    assert not np.isnan(home_lat)
    assert not np.isnan(home_lon)
    assert stats['num_nights'] >= 1
    assert stats['num_points'] >= 1

def test_grid_home_detector_empty():
    import numpy as np
    df = pd.DataFrame({
        'lat': np.array([], dtype=float),
        'lon': np.array([], dtype=float),
        'timestamp': pd.to_datetime([])
    })
    detector = GridHomeDetector()
    home_lat, home_lon, stats = detector.fit(df)
    assert np.isnan(home_lat)
    assert np.isnan(home_lon)
    assert stats['num_nights'] == 0
    assert stats['num_points'] == 0 

def test_grid_based_batch():
    # Two users, each with points
    df = pd.DataFrame({
        'lat': [38.9, 38.9, 38.9001, 39.0, 39.0, 39.0001],
        'lon': [-104.8, -104.8, -104.8001, -105.0, -105.0, -105.0001],
        'timestamp': [
            '2024-07-01T23:30:00', '2024-07-02T01:00:00', '2024-07-02T02:00:00',
            '2024-07-01T23:30:00', '2024-07-02T01:00:00', '2024-07-02T02:00:00'
        ],
        'user_id': ['A', 'A', 'A', 'B', 'B', 'B']
    })
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['lon'], df['lat']), crs="EPSG:4326")
    results = grid_based_batch(gdf, grid_size=20, night_start=22, night_end=6, user_id_col='user_id')
    assert set(results['user_id']) == {'A', 'B'}
    for _, row in results.iterrows():
        assert not pd.isnull(row['lat'])
        assert not pd.isnull(row['lon'])
        assert row['num_nights'] >= 1
        assert row['num_points'] >= 1 
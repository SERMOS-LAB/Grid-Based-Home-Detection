import pandas as pd
import numpy as np
from ghost.algorithms.grid import GridHomeDetector, grid_based_batch
import ghost.algorithms.grid as grid_module
from ghost.preprocessing.projection import project_coordinates
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

def test_grid_home_detector_weekend_fallback():
    # All points are on weekend daytime, none at night
    df = pd.DataFrame({
        'lat': [38.9, 38.9, 38.9001],
        'lon': [-104.8, -104.8, -104.8001],
        'timestamp': [
            '2024-07-06T10:00:00',  # Saturday
            '2024-07-06T12:00:00',
            '2024-07-07T15:00:00'   # Sunday
        ]
    })
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
    home_lat, home_lon, stats = detector.fit(df)
    assert not np.isnan(home_lat)
    assert not np.isnan(home_lon)
    assert stats['inferred_from'] == 'weekend'
    assert stats['num_points'] == 3
    assert stats['stay_time'] > 0

def test_grid_home_detector_stay_time():
    # Points in one cell, check stay_time calculation
    df = pd.DataFrame({
        'lat': [38.9, 38.9, 38.9],
        'lon': [-104.8, -104.8, -104.8],
        'timestamp': [
            '2024-07-01T23:00:00',
            '2024-07-01T23:30:00',
            '2024-07-02T00:00:00'
        ]
    })
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
    home_lat, home_lon, stats = detector.fit(df)
    assert stats['stay_time'] == 3600.0  # 1 hour in seconds
    assert stats['inferred_from'] == 'night'


def test_grid_home_detector_reports_refinement_method():
    df = pd.DataFrame({
        'lat': [38.9, 38.9, 38.9001],
        'lon': [-104.8, -104.8, -104.8001],
        'timestamp': [
            '2024-07-01T23:30:00',
            '2024-07-02T01:00:00',
            '2024-07-02T02:00:00'
        ]
    })
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
    _, _, stats = detector.fit(df)
    assert 'method' in stats
    assert stats['method'].startswith('densest_bin_centroid_') or stats['method'].startswith('mean_cell_points_')


def test_grid_home_detector_falls_back_to_grid_centroid_when_refinement_fails(monkeypatch):
    df = pd.DataFrame({
        'lat': [38.9, 38.9, 38.9001],
        'lon': [-104.8, -104.8, -104.8001],
        'timestamp': [
            '2024-07-01T23:30:00',
            '2024-07-02T01:00:00',
            '2024-07-02T02:00:00'
        ]
    })
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    def _force_refinement_failure(*args, **kwargs):
        return np.nan, np.nan, "forced_failure"

    monkeypatch.setattr(grid_module, 'densest_bin_centroid', _force_refinement_failure)

    detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
    _, _, stats = detector.fit(df)
    assert stats['method'] == 'grid_centroid'


def test_grid_home_detector_refinement_changes_projected_point_from_grid_center():
    # Build clustered points in one grid cell but clearly offset from cell center.
    df = pd.DataFrame({
        'lat': [
            38.90005, 38.90005, 38.90006, 38.90007,  # dense sub-cluster
            38.89995, 38.89994                        # sparse points in same cell
        ],
        'lon': [
            -104.80005, -104.80004, -104.80005, -104.80006,
            -104.79995, -104.79994
        ],
        'timestamp': [
            '2024-07-01T23:00:00',
            '2024-07-01T23:15:00',
            '2024-07-01T23:30:00',
            '2024-07-01T23:45:00',
            '2024-07-02T00:00:00',
            '2024-07-02T00:15:00'
        ]
    })
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
    _, _, stats = detector.fit(df)
    assert stats['method'].startswith('densest_bin_centroid_')

    # Reconstruct the winning cell center and ensure refinement moved off that center.
    prj_lat, prj_lon = project_coordinates(df['lat'], df['lon'], epsg_in=4326, epsg_out=32617)
    tmp = df.copy()
    tmp['prj_lat'] = prj_lat
    tmp['prj_lon'] = prj_lon
    tmp['LAT_Grid'] = np.round(tmp['prj_lat'] / detector.grid_size) * detector.grid_size
    tmp['LON_Grid'] = np.round(tmp['prj_lon'] / detector.grid_size) * detector.grid_size
    tmp['date'] = pd.to_datetime(tmp['timestamp']).dt.date

    per_cell = []
    for (lat_grid, lon_grid), cell_df in tmp.groupby(['LAT_Grid', 'LON_Grid']):
        cell_df = cell_df.sort_values('timestamp')
        stay_time = (
            (cell_df['timestamp'].iloc[-1] - cell_df['timestamp'].iloc[0]).total_seconds()
            if len(cell_df) > 1 else 0.0
        )
        per_cell.append({
            'LAT_Grid': lat_grid,
            'LON_Grid': lon_grid,
            'stay_time': stay_time,
            'num_nights': cell_df['date'].nunique(),
            'num_points': len(cell_df),
        })
    winner = pd.DataFrame(per_cell).sort_values(
        by=['stay_time', 'num_nights', 'num_points'], ascending=False
    ).iloc[0]

    # Refined coordinate should not be exactly equal to the winning center.
    assert not np.isclose(stats['prj_lat'], float(winner['LAT_Grid']), atol=1e-9, rtol=0.0)
    assert not np.isclose(stats['prj_lon'], float(winner['LON_Grid']), atol=1e-9, rtol=0.0)


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
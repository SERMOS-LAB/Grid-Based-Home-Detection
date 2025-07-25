import os
import pandas as pd
import pytest

from ghost.io.gpx import read_gpx
from ghost.io.gpx import read_gpx_folder_to_geodf, read_data
import geopandas as gpd

def test_read_gpx_basic():
    # Path to the sample data.gpx file (relative to project root)
    gpx_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data.gpx'))
    assert os.path.exists(gpx_path), f"Test GPX file not found: {gpx_path}"
    df = read_gpx(gpx_path)
    # Check DataFrame structure
    assert isinstance(df, pd.DataFrame)
    for col in ['timestamp', 'lat', 'lon', 'ele', 'name', 'desc']:
        assert col in df.columns
    # Should have at least one row
    assert len(df) > 0
    # Check types of a sample row
    row = df.iloc[0]
    assert isinstance(row['lat'], float)
    assert isinstance(row['lon'], float)
    # Timestamp can be NaT or pd.Timestamp
    assert pd.isnull(row['timestamp']) or isinstance(row['timestamp'], pd.Timestamp) 

def test_read_data_single_gpx():
    gpx_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data.gpx'))
    if not os.path.exists(gpx_path):
        import pytest; pytest.skip("Test GPX file not found")
    gdf = read_data(gpx_path)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert 'user_id' in gdf.columns
    assert len(gdf) > 0

def test_read_data_csv():
    import pandas as pd
    import tempfile
    df = pd.DataFrame({
        'lat': [1.0, 2.0],
        'lon': [3.0, 4.0],
        'timestamp': pd.to_datetime(['2024-07-01', '2024-07-02']),
        'user_id': ['u1', 'u2']
    })
    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', delete=False) as f:
        df.to_csv(f.name, index=False)
        gdf = read_data(f.name)
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert set(gdf['user_id']) == {'u1', 'u2'}
    os.remove(f.name) 
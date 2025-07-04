import os
import pandas as pd
import pytest

from homegrid.io.gpx import read_gpx

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
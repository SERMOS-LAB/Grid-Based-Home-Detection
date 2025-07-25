import pandas as pd
import numpy as np
from ghost.preprocessing.projection import project_coordinates

def test_project_coordinates_basic():
    lat = pd.Series([38.9, 39.0])
    lon = pd.Series([-104.8, -104.9])
    prj_lat, prj_lon = project_coordinates(lat, lon)
    assert len(prj_lat) == 2 and len(prj_lon) == 2
    assert np.all(pd.notnull(prj_lat))
    assert np.all(pd.notnull(prj_lon))
    assert np.issubdtype(prj_lat.dtype, np.number)
    assert np.issubdtype(prj_lon.dtype, np.number)

def test_project_coordinates_missing():
    lat = pd.Series([38.9, None])
    lon = pd.Series([-104.8, -104.9])
    prj_lat, prj_lon = project_coordinates(lat, lon)
    assert pd.isnull(prj_lat[1])
    assert pd.isnull(prj_lon[1])
    assert pd.notnull(prj_lat[0])
    assert pd.notnull(prj_lon[0]) 
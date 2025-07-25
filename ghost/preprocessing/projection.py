from typing import Tuple
import pandas as pd
from pyproj import Transformer
import numpy as np

def project_coordinates(lat: pd.Series, lon: pd.Series, epsg_in: int = 4326, epsg_out: int = 32617) -> Tuple[pd.Series, pd.Series]:
    """
    Project latitude and longitude to projected coordinates (meters) using pyproj.

    Args:
        lat (pd.Series): Series of latitude values (WGS84).
        lon (pd.Series): Series of longitude values (WGS84).
        epsg_in (int): Input EPSG code (default: 4326, WGS84).
        epsg_out (int): Output EPSG code (default: 32617, UTM zone 17N).

    Returns:
        Tuple[pd.Series, pd.Series]: Projected (Y, X) coordinates in meters as Series. NaN for missing input.

    Example:
        >>> import pandas as pd
        >>> from ghost.preprocessing.projection import project_coordinates
        >>> lat = pd.Series([38.9, None])
        >>> lon = pd.Series([-104.8, -104.8])
        >>> prj_lat, prj_lon = project_coordinates(lat, lon)
        >>> print(prj_lat)
        0    4309708.0
        1          NaN
        dtype: float64
        >>> print(prj_lon)
        0    516888.0
        1         NaN
        dtype: float64
    """
    transformer = Transformer.from_crs(f"epsg:{epsg_in}", f"epsg:{epsg_out}", always_xy=True)
    # Handle missing data gracefully
    mask = lat.notnull() & lon.notnull()
    prj_lat = pd.Series(np.nan, index=lat.index, dtype=float)
    prj_lon = pd.Series(np.nan, index=lon.index, dtype=float)
    if mask.any():
        x, y = transformer.transform(lon[mask].values, lat[mask].values)
        prj_lat[mask] = y
        prj_lon[mask] = x
    return prj_lat, prj_lon 
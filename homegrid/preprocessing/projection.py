from typing import Tuple
import pandas as pd
from pyproj import Transformer
import numpy as np

def project_coordinates(lat: pd.Series, lon: pd.Series, epsg_in: int = 4326, epsg_out: int = 32617) -> Tuple[pd.Series, pd.Series]:
    """
    Project latitude and longitude to meters using pyproj.
    Args:
        lat: Series of latitudes.
        lon: Series of longitudes.
        epsg_in: Input EPSG code (default: 4326).
        epsg_out: Output EPSG code (default: 32617).
    Returns:
        Tuple of (projected_lat, projected_lon) as Series.
    Example:
        >>> import pandas as pd
        >>> from homegrid.preprocessing.projection import project_coordinates
        >>> lat = pd.Series([38.9])
        >>> lon = pd.Series([-104.8])
        >>> prj_lat, prj_lon = project_coordinates(lat, lon)
        >>> print(prj_lat, prj_lon)
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
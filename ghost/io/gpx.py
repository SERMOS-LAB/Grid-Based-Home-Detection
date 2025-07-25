import pandas as pd
from typing import Optional
import gpxpy
import gpxpy.gpx
from datetime import datetime
import geopandas as gpd
import pathlib


# GHOST.io.gpx: GPX and data reading utilities for the GHOST algorithm
def read_gpx(filepath: str) -> pd.DataFrame:
    """
    Parse a GPX file and return a DataFrame for use with the GHOST algorithm.
    Handles waypoints, tracks, and metadata as available.
    Args:
        filepath: Path to the GPX file.
    Returns:
        pd.DataFrame: DataFrame with parsed GPS points.
    Example:
        >>> df = read_gpx('data.gpx')
        >>> print(df.head())
    """
    points = []
    with open(filepath, 'r', encoding='utf-8') as f:
        gpx = gpxpy.parse(f)

    # Waypoints
    for wpt in gpx.waypoints:
        points.append({
            'timestamp': pd.to_datetime(wpt.time) if wpt.time else None,
            'lat': wpt.latitude,
            'lon': wpt.longitude,
            'ele': wpt.elevation if wpt.elevation is not None else None,
            'name': getattr(wpt, 'name', None),
            'desc': getattr(wpt, 'description', None)
        })

    # Track points
    for track in gpx.tracks:
        for segment in track.segments:
            for pt in segment.points:
                points.append({
                    'timestamp': pd.to_datetime(pt.time) if pt.time else None,
                    'lat': pt.latitude,
                    'lon': pt.longitude,
                    'ele': pt.elevation if pt.elevation is not None else None,
                    'name': getattr(pt, 'name', None),
                    'desc': getattr(pt, 'description', None)
                })

    # Route points
    for route in gpx.routes:
        for pt in route.points:
            points.append({
                'timestamp': pd.to_datetime(pt.time) if pt.time else None,
                'lat': pt.latitude,
                'lon': pt.longitude,
                'ele': pt.elevation if pt.elevation is not None else None,
                'name': getattr(pt, 'name', None),
                'desc': getattr(pt, 'description', None)
            })

    df = pd.DataFrame(points)
    # Ensure columns exist even if empty
    for col in ['timestamp', 'lat', 'lon', 'ele', 'name', 'desc']:
        if col not in df.columns:
            df[col] = None
    return df


def read_gpx_folder_to_geodf(folder_path, user_id_col='user_id'):
    """
    Reads a folder of GPX files for GHOST, treating each file as a separate user.
    Returns a GeoDataFrame with a user_id column.

    Args:
        folder_path (str or Path): Path to folder containing GPX files.
        user_id_col (str): Name of the user ID column.

    Returns:
        geopandas.GeoDataFrame: All points with user_id and geometry columns.

    Example:
        >>> from ghost.io.gpx import read_gpx_folder_to_geodf
        >>> gdf = read_gpx_folder_to_geodf('my_gpx_folder')
        >>> print(gdf.head())
    """
    folder = pathlib.Path(folder_path)
    all_points = []
    user_files = list(folder.glob("*.gpx"))
    for gpx_file in user_files:
        df = read_gpx(str(gpx_file))
        if not df.empty:
            df[user_id_col] = gpx_file.stem
            all_points.append(df)
    if not all_points:
        return gpd.GeoDataFrame(columns=['timestamp', 'lat', 'lon', 'ele', 'name', 'desc', user_id_col, 'geometry'], crs="EPSG:4326")
    df_all = pd.concat(all_points, ignore_index=True)
    gdf = gpd.GeoDataFrame(
        df_all,
        geometry=gpd.points_from_xy(df_all['lon'], df_all['lat']),
        crs="EPSG:4326"
    )
    return gdf


def read_data(input_path, user_id_col='user_id', lat_col='lat', lon_col='lon'):
    """
    Generic data reader for CSV, single GPX, or folder of GPX files for GHOST.
    Returns a GeoDataFrame with a user_id column.

    Args:
        input_path (str): Path to file or folder.
        user_id_col (str): Name of user ID column.
        lat_col (str): Latitude column name (for CSV).
        lon_col (str): Longitude column name (for CSV).

    Returns:
        geopandas.GeoDataFrame: Data with user_id and geometry columns.

    Example:
        >>> from ghost.io.gpx import read_data
        >>> gdf = read_data('data.gpx')
        >>> print(gdf.head())
        >>> gdf2 = read_data('my_gpx_folder')
        >>> print(gdf2['user_id'].unique())
    """
    path = pathlib.Path(input_path)
    if path.is_dir():
        return read_gpx_folder_to_geodf(path, user_id_col=user_id_col)
    elif path.suffix.lower() == '.gpx':
        df = read_gpx(str(path))
        df[user_id_col] = path.stem
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df['lon'], df['lat']),
            crs="EPSG:4326"
        )
        return gdf
    elif path.suffix.lower() in ['.csv', '.txt']:
        df = pd.read_csv(str(path))
        if user_id_col not in df.columns:
            df[user_id_col] = 1  # fallback for single-user CSV
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
            crs="EPSG:4326"
        )
        return gdf
    else:
        raise ValueError(f"Unsupported file type or path: {input_path}")


if __name__ == '__main__':
    # Simple usage example
    import sys
    import os
    gpx_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '../../data.gpx')
    df = read_gpx(gpx_file)
    print(df.head()) 
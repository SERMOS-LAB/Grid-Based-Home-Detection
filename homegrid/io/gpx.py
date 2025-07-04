import pandas as pd
from typing import Optional
import gpxpy
import gpxpy.gpx
from datetime import datetime


def read_gpx(filepath: str) -> pd.DataFrame:
    """
    Parse a GPX file and return a DataFrame with columns:
    ['timestamp', 'lat', 'lon', 'ele', 'name', 'desc']
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


if __name__ == '__main__':
    # Simple usage example
    import sys
    import os
    gpx_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '../../data.gpx')
    df = read_gpx(gpx_file)
    print(df.head()) 
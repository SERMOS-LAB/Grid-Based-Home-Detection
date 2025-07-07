import pandas as pd
from typing import Tuple, Dict, Any
from homegrid.preprocessing.projection import project_coordinates
from homegrid.preprocessing.time import extract_time_features
from homegrid.utils import validate_input_dataframe
import numpy as np
from pyproj import Transformer

class GridHomeDetector:
    """
    Grid-based home location detection algorithm.

    Example:
        >>> import pandas as pd
        >>> from homegrid.algorithms.grid import GridHomeDetector
        >>> df = pd.DataFrame({
        ...     'lat': [38.9, 38.9, 38.9001],
        ...     'lon': [-104.8, -104.8, -104.8001],
        ...     'timestamp': ['2024-07-01T23:30:00', '2024-07-02T01:00:00', '2024-07-02T02:00:00']
        ... })
        >>> df['timestamp'] = pd.to_datetime(df['timestamp'])
        >>> detector = GridHomeDetector(grid_size=20, night_start=22, night_end=6)
        >>> home_lat, home_lon, stats = detector.fit(df)
        >>> print(home_lat, home_lon, stats)
    """
    def __init__(self, grid_size: float = 20, night_start: int = 22, night_end: int = 6, epsg_in: int = 4326, epsg_out: int = 32617):
        self.grid_size = grid_size
        self.night_start = night_start
        self.night_end = night_end
        self.epsg_in = epsg_in
        self.epsg_out = epsg_out

    def fit(self, df: pd.DataFrame) -> Tuple[float, float, Dict[str, Any]]:
        """
        Infer home location from GPS data using grid-based clustering.
        Args:
            df: DataFrame with columns ['timestamp', 'lat', 'lon'] (optionally 'ele').
        Returns:
            (home_lat, home_lon, stats_dict)
            - home_lat, home_lon: geographic coordinates (WGS84)
            - stats_dict: includes projected coordinates and other stats
        """
        validate_input_dataframe(df)
        if df.empty or not {'lat', 'lon', 'timestamp'}.issubset(df.columns):
            return np.nan, np.nan, {'num_nights': 0, 'num_points': 0, 'reason': 'empty or missing columns'}

        # Project coordinates
        prj_lat, prj_lon = project_coordinates(df['lat'], df['lon'], epsg_in=self.epsg_in, epsg_out=self.epsg_out)
        df = df.copy()
        df['prj_lat'] = prj_lat
        df['prj_lon'] = prj_lon

        # Extract time features
        df = extract_time_features(df, timestamp_col='timestamp')
        if 'hour' not in df or 'dayofweek' not in df:
            return np.nan, np.nan, {'num_nights': 0, 'num_points': 0, 'reason': 'time extraction failed'}

        # Assign to grid
        df['LAT_Grid'] = np.round(df['prj_lat'] / self.grid_size) * self.grid_size
        df['LON_Grid'] = np.round(df['prj_lon'] / self.grid_size) * self.grid_size

        # Filter to nighttime hours
        night_mask = (df['hour'] >= self.night_start) | (df['hour'] < self.night_end)
        night_df = df[night_mask].copy()
        if night_df.empty:
            return np.nan, np.nan, {'num_nights': 0, 'num_points': 0, 'reason': 'no nighttime points'}

        # Add 'date' column (date only, for unique nights)
        night_df['date'] = pd.to_datetime(night_df['timestamp']).dt.date

        # Group by grid cell, count unique nights and points
        group = night_df.groupby(['LAT_Grid', 'LON_Grid'])
        home_night_signals = group['date'].nunique().reset_index(name='num_nights')
        home_night_signals['num_points'] = group['date'].count().values
        # Sort by most unique nights, then most points
        home_night_signals = home_night_signals.sort_values(by=['num_nights', 'num_points'], ascending=False)

        if home_night_signals.empty:
            return np.nan, np.nan, {'num_nights': 0, 'num_points': 0, 'reason': 'no valid grid cells'}

        prj_home_lat, prj_home_lon, max_num_nights, num_points = home_night_signals.iloc[0][['LAT_Grid', 'LON_Grid', 'num_nights', 'num_points']]

        # Convert projected home location back to lat/lon
        transformer = Transformer.from_crs(f"epsg:{self.epsg_out}", f"epsg:{self.epsg_in}", always_xy=True)
        home_lon, home_lat = transformer.transform(prj_home_lon, prj_home_lat)

        stats = {
            'num_nights': int(max_num_nights),
            'num_points': int(num_points),
            'grid_size': self.grid_size,
            'night_start': self.night_start,
            'night_end': self.night_end,
            'prj_lat': float(prj_home_lat),
            'prj_lon': float(prj_home_lon)
        }
        return home_lat, home_lon, stats 
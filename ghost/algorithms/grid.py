import pandas as pd
from typing import Tuple, Dict, Any
from ghost.preprocessing.projection import project_coordinates
from ghost.preprocessing.time import extract_time_features
from ghost.utils import validate_input_dataframe
import numpy as np
from pyproj import Transformer

# GHOST.algorithms.grid: Core GHOST algorithm implementation
class GridHomeDetector:
    """
    GHOST: Grid-based Home detection via Stay-Time algorithm implementation.

    This detector infers a user's home location from GPS data by:
    - Using nighttime points (default: 22:00–06:00) to find the grid cell with the longest stay-time.
    - If no nighttime points are available, falling back to weekend daytime points (Saturday/Sunday, 08:00–20:00).
    - Stay-time (duration spent in a cell) is used as the primary metric, with unique nights and point count as tie-breakers.

    Example:
        >>> import pandas as pd
        >>> from ghost.algorithms.grid import GridHomeDetector
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
        """
        Initialize the grid-based home detector.
        Args:
            grid_size (float): Grid size in meters.
            night_start (int): Night start hour (24h clock).
            night_end (int): Night end hour (24h clock).
            epsg_in (int): Input EPSG code (default: 4326, WGS84).
            epsg_out (int): Output EPSG code for projection (default: 32617, UTM zone 17N).
        """
        self.grid_size = grid_size
        self.night_start = night_start
        self.night_end = night_end
        self.epsg_in = epsg_in
        self.epsg_out = epsg_out

    def fit(self, df: pd.DataFrame) -> Tuple[float, float, Dict[str, Any]]:
        """
        Infer home location from GPS data using the GHOST algorithm (grid-based clustering with weekend fallback and stay-time calculation).
        Args:
            df (pd.DataFrame): DataFrame with columns ['timestamp', 'lat', 'lon'] (optionally 'ele').
        Returns:
            Tuple[float, float, Dict[str, Any]]: (home_lat, home_lon, stats_dict)
                - home_lat, home_lon: geographic coordinates (WGS84)
                - stats_dict: includes projected coordinates, stay_time, num_nights, num_points, and 'inferred_from' field.
        """
        validate_input_dataframe(df)
        if df.empty or not {'lat', 'lon', 'timestamp'}.issubset(df.columns):
            return np.nan, np.nan, {'num_nights': 0, 'num_points': 0, 'stay_time': 0, 'reason': 'empty or missing columns'}

        # Project coordinates
        prj_lat, prj_lon = project_coordinates(df['lat'], df['lon'], epsg_in=self.epsg_in, epsg_out=self.epsg_out)
        df = df.copy()
        df['prj_lat'] = prj_lat
        df['prj_lon'] = prj_lon

        # Extract time features
        df = extract_time_features(df, timestamp_col='timestamp')
        if 'hour' not in df or 'dayofweek' not in df:
            return np.nan, np.nan, {'num_nights': 0, 'num_points': 0, 'stay_time': 0, 'reason': 'time extraction failed'}

        # Assign to grid
        df['LAT_Grid'] = np.round(df['prj_lat'] / self.grid_size) * self.grid_size
        df['LON_Grid'] = np.round(df['prj_lon'] / self.grid_size) * self.grid_size

        # 1. Nighttime points
        night_mask = (df['hour'] >= self.night_start) | (df['hour'] < self.night_end)
        night_df = df[night_mask].copy()
        night_df['date'] = pd.to_datetime(night_df['timestamp']).dt.date
        if not night_df.empty:
            home_lat, home_lon, stats = self._find_home_by_staytime(night_df)
            stats['inferred_from'] = 'night'
            return home_lat, home_lon, stats

        # 2. Weekend fallback (e.g., 8am–8pm, Sat/Sun)
        weekend_mask = (df['dayofweek'].isin([5, 6])) & (df['hour'] >= 8) & (df['hour'] < 20)
        weekend_df = df[weekend_mask].copy()
        weekend_df['date'] = pd.to_datetime(weekend_df['timestamp']).dt.date
        if not weekend_df.empty:
            home_lat, home_lon, stats = self._find_home_by_staytime(weekend_df)
            stats['inferred_from'] = 'weekend'
            return home_lat, home_lon, stats

        # 3. No data
        return np.nan, np.nan, {'num_nights': 0, 'num_points': 0, 'stay_time': 0, 'reason': 'no nighttime or weekend points'}

    def _find_home_by_staytime(self, df: pd.DataFrame):
        """
        Find the home grid cell by calculating stay-time for each cell (GHOST logic).
        Args:
            df (pd.DataFrame): DataFrame filtered to relevant points (night or weekend), with grid columns.
        Returns:
            Tuple[float, float, Dict[str, Any]]: (home_lat, home_lon, stats_dict)
        """
        # Group by grid cell
        group = df.groupby(['LAT_Grid', 'LON_Grid'])
        stats = []
        for (lat_grid, lon_grid), cell_df in group:
            cell_df = cell_df.sort_values('timestamp')
            # Calculate stay-time (in seconds)
            if len(cell_df) > 1:
                stay_time = (cell_df['timestamp'].iloc[-1] - cell_df['timestamp'].iloc[0]).total_seconds()
            else:
                stay_time = 0.0
            num_nights = cell_df['date'].nunique()
            num_points = len(cell_df)
            stats.append({
                'LAT_Grid': lat_grid,
                'LON_Grid': lon_grid,
                'stay_time': stay_time,
                'num_nights': num_nights,
                'num_points': num_points
            })
        stats_df = pd.DataFrame(stats)
        # Sort by stay_time, then num_nights, then num_points
        stats_df = stats_df.sort_values(by=['stay_time', 'num_nights', 'num_points'], ascending=False)
        best = stats_df.iloc[0]
        prj_home_lat, prj_home_lon = best['LAT_Grid'], best['LON_Grid']
        transformer = Transformer.from_crs(f"epsg:{self.epsg_out}", f"epsg:{self.epsg_in}", always_xy=True)
        home_lon, home_lat = transformer.transform(prj_home_lon, prj_home_lat)
        return home_lat, home_lon, {
            'num_nights': int(best['num_nights']),
            'num_points': int(best['num_points']),
            'stay_time': float(best['stay_time']),
            'prj_lat': float(prj_home_lat),
            'prj_lon': float(prj_home_lon)
        }

def grid_based_batch(gdf, grid_size=20, night_start=22, night_end=6, user_id_col='user_id', epsg_in=4326, epsg_out=32617):
    """
    Applies the grid-based home detection algorithm to a batch of users.
    Args:
        gdf (GeoDataFrame): Preprocessed and projected GeoDataFrame with a user ID column.
        grid_size (int): The grid size in meters.
        night_start (int): Night start hour.
        night_end (int): Night end hour.
        user_id_col (str): The name of the user identifier column.
        epsg_in (int): Input EPSG code.
        epsg_out (int): Output EPSG code.
    Returns:
        DataFrame: One row per user with inferred home location and stats.
    """
    from ghost.utils import validate_input_dataframe
    results = []
    for user_id, user_df in gdf.groupby(user_id_col):
        # Convert to DataFrame for compatibility
        user_df = user_df.copy()
        # Validate and ensure required columns
        try:
            validate_input_dataframe(user_df)
        except Exception as e:
            results.append({
                user_id_col: user_id,
                'lat': None,
                'lon': None,
                'error': str(e)
            })
            continue
        detector = GridHomeDetector(
            grid_size=grid_size,
            night_start=night_start,
            night_end=night_end,
            epsg_in=epsg_in,
            epsg_out=epsg_out
        )
        home_lat, home_lon, stats = detector.fit(user_df)
        row = {
            user_id_col: user_id,
            'lat': home_lat,
            'lon': home_lon,
            **stats
        }
        results.append(row)
    return pd.DataFrame(results) 
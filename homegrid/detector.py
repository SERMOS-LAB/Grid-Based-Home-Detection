import geopandas as gpd
import pandas as pd
from homegrid.io.gpx import read_data
from homegrid.preprocessing.projection import project_coordinates
from homegrid.preprocessing.time import extract_time_features
from homegrid.algorithms.grid import GridHomeDetector, grid_based_batch
from homegrid.config import load_config

class HomeDetector:
    """
    High-level class to detect home locations from GPS data (single-user or batch).

    Initialization supports three modes:
    1. No arguments: uses defaults.
    2. config: pass a config dict (or use from_config_file).
    3. Direct keyword arguments (**kwargs): override any config/defaults.
    4. Mixing config and kwargs: kwargs take precedence.

    Example:
        >>> detector = HomeDetector(grid_size=100)
        >>> detector = HomeDetector(config={'grid_size': 50, 'night_start': 21})
        >>> detector = HomeDetector(config={'grid_size': 50}, grid_size=100)
        >>> detector = HomeDetector.from_config_file('config.yaml')
    """
    def __init__(self, config=None, **kwargs):
        """
        Initializes the detector. 
        Loads parameters from defaults, then config dict, then direct keyword arguments.
        Args:
            config (dict, optional): A dictionary of parameters.
            **kwargs: Direct keyword arguments to override config settings.
        """
        params = self._get_default_config()
        if config:
            params.update(config)
        params.update(kwargs)
        self.config = params
        self.raw_data = None
        self.preprocessed_data = None
        self.results = None

    @classmethod
    def from_config_file(cls, config_path, **kwargs):
        config = load_config(config_path)
        return cls(config, **kwargs)

    def load_data(self):
        """Loads and validates input data as a GeoDataFrame."""
        input_path = self.config.get('input_file')
        user_id_col = self.config.get('user_id_column', 'user_id')
        self.raw_data = read_data(input_path, user_id_col=user_id_col)
        return self

    def preprocess_data(self):
        """Projects coordinates and extracts time features."""
        gdf = self.raw_data.copy()
        # Project coordinates
        epsg_in = self.config.get('epsg_in', 4326)
        epsg_out = self.config.get('epsg_out', 32617)
        prj_lat, prj_lon = project_coordinates(gdf['lat'], gdf['lon'], epsg_in=epsg_in, epsg_out=epsg_out)
        gdf['prj_lat'] = prj_lat
        gdf['prj_lon'] = prj_lon
        # Extract time features
        gdf = extract_time_features(gdf, timestamp_col='timestamp')
        self.preprocessed_data = gdf
        return self

    def detect_homes(self, algorithm='grid'):
        """Runs the selected home detection algorithm (single or batch)."""
        algo = algorithm or self.config.get('algorithm', 'grid')
        user_id_col = self.config.get('user_id_column', 'user_id')
        grid_size = self.config.get('grid_size', 20)
        night_start = self.config.get('night_start', 22)
        night_end = self.config.get('night_end', 6)
        epsg_in = self.config.get('epsg_in', 4326)
        epsg_out = self.config.get('epsg_out', 32617)
        gdf = self.preprocessed_data
        if gdf[user_id_col].nunique() > 1:
            # Batch mode
            self.results = grid_based_batch(
                gdf,
                grid_size=grid_size,
                night_start=night_start,
                night_end=night_end,
                user_id_col=user_id_col,
                epsg_in=epsg_in,
                epsg_out=epsg_out
            )
        else:
            # Single user
            detector = GridHomeDetector(
                grid_size=grid_size,
                night_start=night_start,
                night_end=night_end,
                epsg_in=epsg_in,
                epsg_out=epsg_out
            )
            home_lat, home_lon, stats = detector.fit(gdf)
            row = {
                user_id_col: gdf[user_id_col].iloc[0],
                'lat': home_lat,
                'lon': home_lon,
                **stats
            }
            self.results = pd.DataFrame([row])
        return self

    def get_results(self):
        """Returns the final DataFrame of home locations."""
        return self.results

    def _get_default_config(self):
        return {
            'grid_size': 20,
            'night_start': 22,
            'night_end': 6,
            'epsg_in': 4326,
            'epsg_out': 32617,
            'user_id_column': 'user_id',
            'input_file': None,
            'algorithm': 'grid'
        } 
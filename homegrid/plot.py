# homegrid.plot: Visualization utilities

import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional

# Optional imports for basemap and interactive
try:
    import contextily as ctx
except ImportError:
    ctx = None
try:
    import folium
except ImportError:
    folium = None

def plot_tracks(df):
    """
    Plot GPS tracks from a DataFrame.
    """
    # Implementation to be added
    raise NotImplementedError("Track plotting not yet implemented.")

def plot_gps_points(df: pd.DataFrame, ax: Optional[plt.Axes] = None, color: str = 'blue', alpha: float = 0.5, s: int = 10, basemap: bool = False, crs: str = 'epsg:4326', **kwargs):
    """
    Plot GPS points using matplotlib. Optionally add a basemap (requires contextily and projected CRS).
    Args:
        df: DataFrame with 'lat' and 'lon' columns.
        ax: Optional matplotlib Axes.
        color: Point color.
        alpha: Point transparency.
        s: Marker size.
        basemap: If True, add OSM basemap (requires contextily and projected CRS).
        crs: CRS of input data ('epsg:4326' for lat/lon, 'epsg:3857' for web mercator).
        **kwargs: Passed to plt.scatter.
    Returns:
        ax: The matplotlib Axes.
    Example:
        >>> plot_gps_points(df)
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    x = df['lon']
    y = df['lat']
    if crs == 'epsg:3857':
        x = df['lon']
        y = df['lat']
    ax.scatter(x, y, c=color, alpha=alpha, s=s, label='GPS points', **kwargs)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    if basemap and ctx is not None and crs == 'epsg:3857':
        ctx.add_basemap(ax, crs=crs)
    return ax

def plot_home_location(ax: plt.Axes, home_lat: float, home_lon: float, color: str = 'red', marker: str = 'X', label: str = 'Home', **kwargs):
    """
    Overlay the inferred home location on a matplotlib plot.
    Args:
        ax: Matplotlib Axes.
        home_lat: Latitude of home.
        home_lon: Longitude of home.
        color: Marker color.
        marker: Marker style.
        label: Legend label.
        **kwargs: Passed to plt.scatter.
    Returns:
        ax: The matplotlib Axes.
    Example:
        >>> plot_home_location(ax, 38.9, -104.8)
    """
    ax.scatter([home_lon], [home_lat], c=color, marker=marker, s=100, label=label, **kwargs)
    return ax

def plot_full_result(df: pd.DataFrame, home_lat: float, home_lon: float, gt_lat: Optional[float] = None, gt_lon: Optional[float] = None, basemap: bool = False, crs: str = 'epsg:4326', save_path: Optional[str] = None):
    """
    Plot GPS points, inferred home, and optionally ground truth on a map.
    Args:
        df: DataFrame with 'lat' and 'lon'.
        home_lat, home_lon: Inferred home location.
        gt_lat, gt_lon: Ground truth location (optional).
        basemap: If True, add OSM basemap (requires contextily and projected CRS).
        crs: CRS of input data ('epsg:4326' or 'epsg:3857').
        save_path: If provided, save the plot to this file.
    Returns:
        fig, ax: Matplotlib Figure and Axes.
    Example:
        >>> plot_full_result(df, home_lat, home_lon)
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    plot_gps_points(df, ax=ax, basemap=basemap, crs=crs)
    plot_home_location(ax, home_lat, home_lon)
    if gt_lat is not None and gt_lon is not None:
        ax.scatter([gt_lon], [gt_lat], c='green', marker='*', s=120, label='Ground Truth')
    ax.legend()
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
    return fig, ax

def plot_interactive_map(df: pd.DataFrame, home_lat: float, home_lon: float, gt_lat: Optional[float] = None, gt_lon: Optional[float] = None, zoom_start: int = 14) -> Optional['folium.Map']:
    """
    Create an interactive map with folium showing GPS points, inferred home, and optionally ground truth.
    Args:
        df: DataFrame with 'lat' and 'lon'.
        home_lat, home_lon: Inferred home location.
        gt_lat, gt_lon: Ground truth location (optional).
        zoom_start: Initial zoom level.
    Returns:
        folium.Map object (or None if folium not installed)
    Example:
        >>> m = plot_interactive_map(df, home_lat, home_lon)
        >>> m.save('map.html')
    """
    if folium is None:
        print("folium is not installed.")
        return None
    center = [home_lat, home_lon]
    m = folium.Map(location=center, zoom_start=zoom_start)
    # Plot GPS points
    for _, row in df.iterrows():
        folium.CircleMarker(location=[row['lat'], row['lon']], radius=3, color='blue', fill=True, fill_opacity=0.5).add_to(m)
    # Plot inferred home
    folium.Marker(location=[home_lat, home_lon], icon=folium.Icon(color='red', icon='home'), popup='Inferred Home').add_to(m)
    # Plot ground truth
    if gt_lat is not None and gt_lon is not None:
        folium.Marker(location=[gt_lat, gt_lon], icon=folium.Icon(color='green', icon='star'), popup='Ground Truth').add_to(m)
    return m 
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
from ghost.plot import plot_gps_points, plot_home_location, plot_full_result, plot_interactive_map

def test_plot_gps_points_runs():
    df = pd.DataFrame({'lat': [38.9, 38.9001], 'lon': [-104.8, -104.8001]})
    ax = plot_gps_points(df)
    assert ax is not None

def test_plot_home_location_runs():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax = plot_home_location(ax, 38.9, -104.8)
    assert ax is not None

def test_plot_full_result_runs():
    df = pd.DataFrame({'lat': [38.9, 38.9001], 'lon': [-104.8, -104.8001]})
    fig, ax = plot_full_result(df, 38.9, -104.8)
    assert fig is not None and ax is not None

def test_plot_interactive_map_runs():
    df = pd.DataFrame({'lat': [38.9, 38.9001], 'lon': [-104.8, -104.8001]})
    m = plot_interactive_map(df, 38.9, -104.8)
    # If folium is not installed, m is None; otherwise, it's a folium.Map
    assert m is None or hasattr(m, 'save') 
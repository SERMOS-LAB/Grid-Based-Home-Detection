import pandas as pd
import numpy as np
import tempfile
import os
from homegrid.validation.groundtruth import load_groundtruth_csv, compare_predictions_to_groundtruth

def test_load_groundtruth_csv(tmp_path):
    # Create a temporary CSV
    data = pd.DataFrame({'user_id': [1, 2], 'lat': [38.9, 39.0], 'lon': [-104.8, -104.9]})
    csv_path = tmp_path / 'gt.csv'
    data.to_csv(csv_path, index=False)
    df = load_groundtruth_csv(str(csv_path))
    assert set(['user_id', 'lat', 'lon']).issubset(df.columns)
    assert len(df) == 2

def test_compare_predictions_to_groundtruth():
    pred = pd.DataFrame({'user_id': [1], 'lat': [38.9], 'lon': [-104.8]})
    gt = pd.DataFrame({'user_id': [1], 'lat': [38.9001], 'lon': [-104.8001]})
    df = compare_predictions_to_groundtruth(pred, gt)
    assert 'error_m' in df.columns
    assert df.shape[0] == 1
    assert 0 < df.loc[0, 'error_m'] < 20 
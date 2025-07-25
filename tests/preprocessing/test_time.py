import pandas as pd
import numpy as np
from ghost.preprocessing.time import extract_time_features

def test_extract_time_features_basic():
    df = pd.DataFrame({'timestamp': pd.to_datetime(['2024-07-01T23:00:00', '2024-07-02T08:15:00'])})
    df2 = extract_time_features(df)
    assert 'hour' in df2.columns and 'dayofweek' in df2.columns
    assert df2.loc[0, 'hour'] == 23
    assert df2.loc[1, 'hour'] == 8
    assert df2.loc[0, 'dayofweek'] == 0  # Monday
    assert df2.loc[1, 'dayofweek'] == 1  # Tuesday

def test_extract_time_features_missing():
    df = pd.DataFrame({'timestamp': [pd.NaT, '2024-07-03T12:00:00']})
    df2 = extract_time_features(df)
    assert np.isnan(df2.loc[0, 'hour'])
    assert np.isnan(df2.loc[0, 'dayofweek'])
    assert df2.loc[1, 'hour'] == 12
    assert df2.loc[1, 'dayofweek'] == 2  # Wednesday 
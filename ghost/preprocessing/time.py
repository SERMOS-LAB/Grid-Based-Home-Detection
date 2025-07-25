import pandas as pd

def extract_time_features(df: pd.DataFrame, timestamp_col: str = 'timestamp') -> pd.DataFrame:
    """
    Add 'hour' and 'dayofweek' columns to a DataFrame based on a timestamp column.

    Args:
        df (pd.DataFrame): DataFrame with a timestamp column.
        timestamp_col (str): Name of the timestamp column (default: 'timestamp').

    Returns:
        pd.DataFrame: Copy of the input DataFrame with added 'hour' (0-23) and 'dayofweek' (0=Monday, 6=Sunday) columns.

    Example:
        >>> import pandas as pd
        >>> from ghost.preprocessing.time import extract_time_features
        >>> df = pd.DataFrame({'timestamp': pd.to_datetime(['2024-07-01T23:00:00', '2024-07-02T08:15:00'])})
        >>> df2 = extract_time_features(df)
        >>> print(df2[['timestamp', 'hour', 'dayofweek']])
             timestamp  hour  dayofweek
        0 2024-07-01 23:00:00    23          0
        1 2024-07-02 08:15:00     8          1
    Note:
        The original DataFrame is not modified; a copy is returned.
    """
    df = df.copy()
    # Ensure timestamp column is datetime
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
    df['hour'] = df[timestamp_col].dt.hour
    df['dayofweek'] = df[timestamp_col].dt.dayofweek
    return df 
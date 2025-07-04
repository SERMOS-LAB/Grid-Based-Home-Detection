import pandas as pd

def extract_time_features(df: pd.DataFrame, timestamp_col: str = 'timestamp') -> pd.DataFrame:
    """
    Add 'hour' and 'dayofweek' columns to the DataFrame based on the timestamp column.
    Args:
        df: DataFrame with a timestamp column.
        timestamp_col: Name of the timestamp column.
    Returns:
        DataFrame with added 'hour' and 'dayofweek' columns.
    Example:
        >>> import pandas as pd
        >>> from homegrid.preprocessing.time import extract_time_features
        >>> df = pd.DataFrame({'timestamp': pd.to_datetime(['2024-07-01T23:00:00', '2024-07-02T08:15:00'])})
        >>> df = extract_time_features(df)
        >>> print(df[['timestamp', 'hour', 'dayofweek']])
    """
    df = df.copy()
    # Ensure timestamp column is datetime
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
    df['hour'] = df[timestamp_col].dt.hour
    df['dayofweek'] = df[timestamp_col].dt.dayofweek
    return df 
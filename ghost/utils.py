# GHOST.utils: Miscellaneous helpers for the GHOST algorithm

import pandas as pd

def validate_input_dataframe(df: pd.DataFrame, required_columns=None):
    """
    Validate that the input DataFrame has the required columns and types for GHOST processing.

    Args:
        df (pd.DataFrame): Input DataFrame.
        required_columns (list, optional): List of required columns (default: ['timestamp', 'lat', 'lon'])

    Raises:
        ValueError: If columns are missing or types are incorrect.

    Example:
        >>> import pandas as pd
        >>> from ghost.utils import validate_input_dataframe
        >>> df = pd.DataFrame({'timestamp': pd.to_datetime(['2024-07-01']), 'lat': [38.9], 'lon': [-104.8]})
        >>> validate_input_dataframe(df)  # Passes
        >>> df2 = pd.DataFrame({'lat': [38.9], 'lon': [-104.8]})
        >>> validate_input_dataframe(df2)  # Raises ValueError: Input data is missing required columns: ['timestamp']
    """
    if required_columns is None:
        required_columns = ['timestamp', 'lat', 'lon']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Input data is missing required columns: {missing}. "
                         f"Expected columns: {required_columns}")
    # Type checks (optional, can be expanded)
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        raise ValueError("'timestamp' column must be datetime type. Use pd.to_datetime to convert.")
    if not pd.api.types.is_float_dtype(df['lat']):
        raise ValueError("'lat' column must be float type.")
    if not pd.api.types.is_float_dtype(df['lon']):
        raise ValueError("'lon' column must be float type.") 
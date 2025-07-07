# homegrid.utils: Miscellaneous helpers 

import pandas as pd

def validate_input_dataframe(df: pd.DataFrame, required_columns=None):
    """
    Validate that the input DataFrame has the required columns and types.
    Args:
        df: Input DataFrame.
        required_columns: List of required columns (default: ['timestamp', 'lat', 'lon'])
    Raises:
        ValueError if columns are missing or types are incorrect.
    Example:
        >>> validate_input_dataframe(df)
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
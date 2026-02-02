from __future__ import annotations

from pathlib import Path
import pandas as pd


def load_data(csv_path: str | Path) -> pd.DataFrame:
    """
    Load the maternal health dataset from a CSV file.

    Parameters
    ----------
    csv_path : str | Path
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded dataframe.
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path.resolve()}")

    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError("Loaded dataframe is empty. Check the CSV content.")

    return df

import pandas as pd
from typing import List
from pathlib import Path


def xlsx_to_string_list(file_path: str | Path, column_index: int = 0, sheet_name: int | str = 0, skip_header: bool = False) -> List[str]:
    """
    Reads a single column from an Excel (.xlsx) file and converts it to a list of Python strings.
    
    Args:
        file_path: Path to the .xlsx file (string or Path object)
        column_index: Index of the column to read (default: 0 for first column)
        sheet_name: Name or index of the sheet to read (default: 0 for first sheet)
        skip_header: Whether to skip the first row (header) (default: False)
    
    Returns:
        List[str]: List of strings from the specified column
    
    Example:
        >>> strings = xlsx_to_string_list('data.xlsx')
        >>> strings = xlsx_to_string_list('data.xlsx', column_index=0, skip_header=True)
    """
    # Convert string path to Path object if needed
    file_path = Path(file_path) if isinstance(file_path, str) else file_path
    
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None if not skip_header else 0)
    
    # Extract the specified column and convert to list of strings
    # Handle NaN values by converting them to empty strings
    column_data = df.iloc[:, column_index].astype(str).replace('nan', '').tolist()
    
    # Filter out empty strings if desired (optional)
    # column_data = [s for s in column_data if s.strip()]
    
    return column_data


def xlsx_to_three_columns(file_path: str | Path, sheet_name: int | str = 0, skip_header: bool = False) -> tuple[List[str], List[str], List[str]]:
    """
    Reads three columns from an Excel (.xlsx) file and returns them as three separate lists of strings.
    
    Args:
        file_path: Path to the .xlsx file (string or Path object)
        sheet_name: Name or index of the sheet to read (default: 0 for first sheet)
        skip_header: Whether to skip the first row (header) (default: False)
    
    Returns:
        tuple[List[str], List[str], List[str]]: Tuple containing three lists of strings (column 0, column 1, column 2)
    
    Example:
        >>> col1, col2, col3 = xlsx_to_three_columns('data.xlsx')
        >>> col1, col2, col3 = xlsx_to_three_columns('data.xlsx', skip_header=True)
    """
    # Convert string path to Path object if needed
    file_path = Path(file_path) if isinstance(file_path, str) else file_path
    
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None if not skip_header else 0)
    
    # Extract the first three columns and convert to lists of strings
    # Handle NaN values by converting them to empty strings
    col1 = df.iloc[:, 0].astype(str).replace('nan', '').tolist()
    col2 = df.iloc[:, 1].astype(str).replace('nan', '').tolist()
    col3 = df.iloc[:, 2].astype(str).replace('nan', '').tolist()
    
    return col1, col2, col3


if __name__ == "__main__":
    # Use raw string (r"...") to avoid Windows path escape sequence issues
    # The r prefix tells Python to treat backslashes as literal characters
    brand_order = xlsx_to_string_list(r"C:\Users\resea\OneDrive\Desktop\order.xlsx")
    print(brand_order)
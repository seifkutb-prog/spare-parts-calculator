import pandas as pd


def load_parts(filepath):
    """
    Reads the spare parts Excel file and returns a list of dictionaries.
    Each dictionary is one spare part with all its data.
    """
    print(f'Loading data from: {filepath}')

    try:
        df = pd.read_excel(filepath)
    except FileNotFoundError:
        print(f'ERROR: Could not find file: {filepath}')
        print('Make sure the file path is correct and try again.')
        exit(1)

    # Check that required columns exist
    required_columns = ['part_name', 'monthly_faults', 'months_recorded',
                        'lead_time_days', 'max_demand', 'unit_cost']
    for col in required_columns:
        if col not in df.columns:
            print(f'ERROR: Missing column in Excel file: {col}')
            print(f'Your file has these columns: {list(df.columns)}')
            exit(1)

    # Convert to list of dictionaries
    parts = df.to_dict(orient='records')
    print(f'Successfully loaded {len(parts)} spare parts.')
    return parts


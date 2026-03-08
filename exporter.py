import pandas as pd
from datetime import datetime


def export_results(results, output_path, station_name):
    """
    Takes the calculated results and saves them to a formatted Excel file.
    """
    # Build a clean DataFrame for export
    export_data = []
    for item in results:
        export_data.append({
            'Part Name':          item['part_name'],
            'Consumption Rate/Mo':item['consumption_rate'],
            'Reorder Point':      item['reorder_point'],
            'Safety Stock':       item['safety_stock'],
            'Recommended Qty':    item['recommended_qty'],
            'Unit Cost (EGP)':    item.get('unit_cost', 0),
            'Total Value (EGP)':  round(item['recommended_qty'] * item.get('unit_cost',0), 2)
        })

    df = pd.DataFrame(export_data)

    # Write to Excel with formatting
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'{station_name}_Report')

    print(f'Results saved to: {output_path}')
    print(f'Total parts processed: {len(results)}')
    print(f'Total recommended inventory value: EGP {df["Total Value (EGP)"].sum():,.2f}')


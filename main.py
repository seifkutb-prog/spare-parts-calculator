import argparse
from calculator import (
    calculate_consumption_rate,
    calculate_reorder_point,
    calculate_safety_stock,
    calculate_recommended_qty
)
from data_loader import load_parts
from exporter import export_results


def process_parts(parts):
    """Run calculations on every spare part in the list."""
    results = []
    for part in parts:
        try:
            rate = calculate_consumption_rate(
                part['monthly_faults'], part['months_recorded']
            )
            daily_rate = rate / 30
            rop  = calculate_reorder_point(daily_rate, part['lead_time_days'])
            ss   = calculate_safety_stock(
                part['max_demand'], rate, part['lead_time_days']
            )
            qty  = calculate_recommended_qty(rop, ss)
            results.append({
                **part,
                'consumption_rate': rate,
                'reorder_point':    rop,
                'safety_stock':     ss,
                'recommended_qty':  qty,
            })
        except ValueError as e:
            print(f'WARNING: Skipping {part["part_name"]} — {e}')
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Spare Parts Reorder Calculator for Rolling Stock Maintenance'
    )
    parser.add_argument('--input',   required=True,  help='Path to input Excel file')
    parser.add_argument('--output',  default='results.xlsx', help='Output file name')
    parser.add_argument('--station', default='Depot', help='Station/Depot name')
    args = parser.parse_args()

    print('='*60)
    print('  Spare Parts Reorder Calculator')
    print(f'  Station: {args.station}')
    print('='*60)

    parts   = load_parts(args.input)
    results = process_parts(parts)
    export_results(results, args.output, args.station)

    print('='*60)
    print('  DONE! Open your output file to see the results.')
    print('='*60)


if __name__ == '__main__':
    main()


from calculator import (
    calculate_consumption_rate,
    calculate_reorder_point,
    calculate_safety_stock,
    calculate_eoq,
    calculate_turnover_rate,
    calculate_recommended_qty,
)

# Standard ordering cost assumption (EGP per purchase order)
ORDERING_COST = 250
# Standard holding cost as % of unit cost per year
HOLDING_COST_PCT = 0.20


def classify_abc(parts):
    """
    ABC Analysis — classify parts by annual value consumption.
    Sort all parts by (consumption_rate × unit_cost) descending.
    Top 80% of total value  = Class A  (critical, tightest control)
    Next 15% of total value = Class B  (moderate control)
    Bottom 5% of total value= Class C  (low value, bulk order)
    """
    for part in parts:
        part['annual_value'] = round(part['consumption_rate'] * 12 * part.get('unit_cost', 0), 2)

    parts.sort(key=lambda x: x['annual_value'], reverse=True)
    total_value = sum(p['annual_value'] for p in parts)

    if total_value == 0:
        for part in parts:
            part['abc_class'] = 'C'
        return parts

    cumulative = 0
    for part in parts:
        cumulative += part['annual_value']
        pct = (cumulative / total_value) * 100
        if pct <= 80:
            part['abc_class'] = 'A'
        elif pct <= 95:
            part['abc_class'] = 'B'
        else:
            part['abc_class'] = 'C'

    return parts


def process_all_parts(parts):
    """
    Run all calculations on every spare part.
    Returns enriched list + summary statistics.
    """
    results = []

    for part in parts:
        try:
            rate       = calculate_consumption_rate(part['monthly_faults'], part['months_recorded'])
            daily_rate = rate / 30
            rop        = calculate_reorder_point(daily_rate, part['lead_time_days'])
            ss         = calculate_safety_stock(part['max_demand'], rate, part['lead_time_days'])
            qty        = calculate_recommended_qty(rop, ss)
            annual_dem = rate * 12
            holding_c  = part.get('unit_cost', 0) * HOLDING_COST_PCT
            eoq        = calculate_eoq(annual_dem, ORDERING_COST, holding_c)
            avg_stock  = qty / 2 if qty > 0 else 1
            turnover   = calculate_turnover_rate(rate, avg_stock)
            total_val  = round(qty * part.get('unit_cost', 0), 2)

            results.append({
                **part,
                'consumption_rate':  rate,
                'reorder_point':     rop,
                'safety_stock':      ss,
                'recommended_qty':   qty,
                'eoq':               int(eoq),
                'turnover_rate':     turnover,
                'annual_value':      round(annual_dem * part.get('unit_cost', 0), 2),
                'total_stock_value': total_val,
            })
        except (ValueError, ZeroDivisionError) as e:
            results.append({**part, 'error': str(e),
                'consumption_rate':0,'reorder_point':0,'safety_stock':0,
                'recommended_qty':0,'eoq':0,'turnover_rate':0,
                'annual_value':0,'total_stock_value':0})

    results = classify_abc(results)

    # Summary statistics
    valid = [r for r in results if 'error' not in r]
    summary = {
        'total_parts':       len(results),
        'class_a':           sum(1 for r in valid if r['abc_class']=='A'),
        'class_b':           sum(1 for r in valid if r['abc_class']=='B'),
        'class_c':           sum(1 for r in valid if r['abc_class']=='C'),
        'total_stock_value': round(sum(r['total_stock_value'] for r in valid), 2),
        'avg_turnover':      round(sum(r['turnover_rate'] for r in valid)/len(valid),2) if valid else 0,
        'errors':            len(results) - len(valid),
    }

    return results, summary


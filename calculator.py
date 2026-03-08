import math

def calculate_consumption_rate(total_faults, months):
    """Average monthly consumption rate."""
    if months <= 0:
        raise ValueError(f'Months must be > 0, got {months}')
    return round(total_faults / months, 3)


def calculate_reorder_point(avg_daily_consumption, lead_time_days):
    """Stock level at which a new order must be placed."""
    return round(avg_daily_consumption * lead_time_days, 1)


def calculate_safety_stock(max_demand, avg_demand, lead_time):
    """Buffer stock to absorb demand variation."""
    return round(max(0, (max_demand - avg_demand) * lead_time), 1)


def calculate_eoq(annual_demand, ordering_cost, holding_cost_per_unit):
    """
    Economic Order Quantity — the optimal order size that
    minimizes total inventory cost.
    Formula: EOQ = sqrt( (2 × D × S) / H )
      D = Annual demand (units/year)
      S = Cost per order (ordering cost)
      H = Holding cost per unit per year
    """
    if holding_cost_per_unit <= 0 or annual_demand <= 0:
        return 0
    return round(math.sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit), 0)


def calculate_turnover_rate(consumption_rate, avg_stock):
    """
    How many times stock is fully consumed and replenished per year.
    High turnover = fast moving = good.
    Low turnover = slow moving = dead stock risk.
    """
    if avg_stock <= 0:
        return 0
    annual_consumption = consumption_rate * 12
    return round(annual_consumption / avg_stock, 2)


def calculate_recommended_qty(reorder_point, safety_stock):
    """Total quantity to keep in stock."""
    return int(reorder_point + safety_stock)



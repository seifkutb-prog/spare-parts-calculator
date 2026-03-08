def calculate_consumption_rate(total_faults, months):
    """
    How many faults happen per month on average.
    Example: 12 faults over 6 months = 2 faults/month
    """
    if months <= 0:
        raise ValueError(f'Months must be greater than zero. Got: {months}')
    return round(total_faults / months, 2)


def calculate_reorder_point(avg_daily_consumption, lead_time_days):
    """
    The stock level at which you must place a new order.
    Formula: Average daily use × Lead time in days
    """
    if lead_time_days < 0:
        raise ValueError(f'Lead time cannot be negative. Got: {lead_time_days}')
    return round(avg_daily_consumption * lead_time_days, 0)


def calculate_safety_stock(max_demand, avg_demand, lead_time):
    """
    Extra buffer stock to handle unexpected demand spikes.
    Formula: (Max demand - Average demand) × Lead time
    """
    return round(max(0, (max_demand - avg_demand) * lead_time), 0)


def calculate_recommended_qty(reorder_point, safety_stock):
    """
    Total quantity to keep in stock at all times.
    """
    return int(reorder_point + safety_stock)


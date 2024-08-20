# %%
import pandas as pd
import numpy as np
from datetime import date, timedelta
from scipy import interpolate

"""
This script calculates forward rates for various tenors based on a given yield curve.
It uses interpolation to estimate rates for periods not directly provided in the input data.
"""

current_yields = {
    '1M': 0.05333,
    '3M': 0.051728,
    '6M': 0.049086,
    '1Y': 0.04505,
    '2Y': 0.04004,
    '3Y': 0.038071,
    '5Y': 0.037039,
    '10Y': 0.038246,
    '20Y': 0.041854,
    '30Y': 0.040717
}

def interpolate_rate(tenors, rates, target_tenor):
    """
    Interpolate the rate for a given tenor using cubic interpolation.

    Args:
        tenors (list): List of known tenors in years.
        rates (list): List of known rates corresponding to the tenors.
        target_tenor (float): The tenor for which to interpolate the rate, in years.

    Returns:
        float: The interpolated rate for the target tenor.
    """
    f = interpolate.interp1d(tenors, rates, kind='cubic', fill_value='extrapolate')
    return float(f(target_tenor))

def calculate_forward_rate(r1, r2, t1, t2):
    """
    Calculate the forward rate between two time periods.

    Args:
        r1 (float): Rate at time t1.
        r2 (float): Rate at time t2.
        t1 (float): Start time in years.
        t2 (float): End time in years.

    Returns:
        float: The calculated forward rate.
    """
    return ((1 + r2)**t2 / (1 + r1)**t1)**(1 / (t2 - t1)) - 1

def generate_dates(start_date, num_months):
    """
    Generate a list of dates for each month starting from the given start date.

    Args:
        start_date (date): The starting date.
        num_months (int): The number of months to generate dates for.

    Returns:
        list: A list of dates, one for each month.
    """
    return [start_date + timedelta(days=30*i) for i in range(num_months)]

def get_monthly_forward_rates(yields, num_months=60, start_date=None):
    """
    Calculate forward rates for each tenor at monthly intervals.

    Args:
        yields (dict): Dictionary of current yields, with tenors as keys and rates as values.
        num_months (int, optional): Number of months to calculate forward rates for. Defaults to 60.
        start_date (date, optional): Starting date for calculations. Defaults to today if not provided.

    Returns:
        pandas.DataFrame: DataFrame of forward rates indexed by date, with columns for each tenor.
    """
    if start_date is None:
        start_date = date.today()
    
    tenors = list(yields.keys())
    tenor_years = {'1M': 1/12, '3M': 1/4, '6M': 1/2, '1Y': 1, '2Y': 2, '3Y': 3, '5Y': 5, '10Y': 10, '20Y': 20, '30Y': 30}
    
    all_monthly_tenors = [i/12 for i in range(1, int(max(tenor_years.values())*12) + 1)]
    
    known_tenors = [tenor_years[t] for t in tenors]
    known_rates = list(yields.values())
    interpolated_rates = [interpolate_rate(known_tenors, known_rates, t) for t in all_monthly_tenors]
    
    dates = generate_dates(start_date, num_months)
    
    forward_rates = pd.DataFrame(index=dates, columns=tenors)
    
    for i, current_date in enumerate(dates):
        for tenor in tenors:
            t1 = i / 12
            t2 = t1 + tenor_years[tenor]
            r1 = interpolate_rate(all_monthly_tenors, interpolated_rates, t1)
            r2 = interpolate_rate(all_monthly_tenors, interpolated_rates, t2)
            forward_rate = calculate_forward_rate(r1, r2, t1, t2)
            forward_rates.loc[current_date, tenor] = forward_rate
    
    return forward_rates

# Calculate forward rates for 60 months starting from today
start_date = date.today()
forward_rates = get_monthly_forward_rates(current_yields, num_months=60, start_date=start_date)

# Display the first few rows of the results
print("Forward Rates for Each Tenor by Date:")
print(forward_rates.head().applymap(lambda x: f"{x:.2%}"))






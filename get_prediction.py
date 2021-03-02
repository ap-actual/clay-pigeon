import yfinance as yf
import numpy as np
import datetime as dt
import pandas as pd


def get_prediction(reference, td_year, td_month, td_day, rf_year, benchmark):

    # Get day of week & week of year
    td_week = dt.date(td_year, td_month, td_day).isocalendar()[1]
    td_day_of_week = dt.date(td_year,td_month,td_day).weekday()

    # reduce reference df to within two years to prevent ambiguity when searching for day of week / week of year
    d1 = str(int(rf_year-1)) + '-01-01'
    d2 = str(int(rf_year+1)) + '-01-01'
    reference2 = reference.loc[d1:d2]

    # find nth day prior to analysis of target with day of week and week of year
    ref_end_ii = np.where(
        np.logical_and(reference2['day_of_week'] == td_day_of_week, reference2['week_num'] == td_week))

    # select first entry if search yields more than one result
    if len(ref_end_ii[0]) > 1:
        ref_end_i = ref_end_ii[0][len(ref_end_ii)]
    else:
        ref_end_i = ref_end_ii[0][0]

    predicted_percent_close = reference2['percent_close'].iloc[ref_end_i]
    predicted_percent_high = reference2['percent_high'].iloc[ref_end_i]

    sendit = np.array([predicted_percent_close, predicted_percent_high])

    return sendit

# script to pull data from yfinance

# Import the plotting library
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import numpy as np
import datetime as dt
from normalize_tick import normalize_tick


def get_diff(reference, target, trade_days_prior, td_year, td_month, td_day):

    # Get day of week & week of year
    td_week = dt.date(td_year, td_month, td_day).isocalendar()[1]
    td_day_of_week = dt.date(td_year,td_month,td_day).weekday()

    # find nth day prior to analysis of target
    ref_end_ii = np.where(np.logical_and(reference['day_of_week'] == td_day_of_week-1, reference['week_num'] == td_week))
    ref_end_i = ref_end_ii[0][1:]
    tar_end_ii = np.where(np.logical_and(target['day_of_week'] == td_day_of_week-1, target['week_num'] == td_week))
    tar_end_i = tar_end_ii[0]
    tar_start_i = tar_end_i - trade_days_prior

    tar_dat = target.iloc[tar_start_i[0]:tar_end_i[0], :]

    tar_dat_arr_ph = tar_dat['percent_high'].to_numpy()
    tar_dat_arr_pl = tar_dat['percent_low'].to_numpy()
    tar_dat_arr_pc = tar_dat['percent_close'].to_numpy()

    diff = np.ones((len(ref_end_i),4))  # 4x1 array to store difference in percent high, low, and close
    n = 0
    for i in ref_end_i:
        ref_start_i = i - trade_days_prior
        ref_dat = reference.iloc[ref_start_i:i, :]
        diff[n, 0] = ref_dat.iloc[0]['Date'].year
        ref_dat_arr = ref_dat['percent_high'].to_numpy()
        diff[n, 1] = sum(abs(ref_dat_arr - tar_dat_arr_ph))
        ref_dat_arr = ref_dat['percent_low'].to_numpy()
        diff[n, 2] = sum(abs(ref_dat_arr - tar_dat_arr_pl))
        ref_dat_arr = ref_dat['percent_close'].to_numpy()
        diff[n, 3] = sum(abs(ref_dat_arr - tar_dat_arr_pc))
        n = n+1

    return diff

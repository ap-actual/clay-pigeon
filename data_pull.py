# script to pull data from yfinance

# Import the plotting library
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import numpy as np
import datetime as dt

def get_diff(reference, tar_tick, trade_days_prior, td_year, td_month, td_day):

    # Get day of week & week of year
    td_week = dt.date(td_year, td_month, td_day).isocalendar()[1]
    td_day_of_week = dt.date(td_year,td_month,td_day).weekday()


    # Get the data of target stock
    # TODO  put in error handling
    tick = yf.Ticker(tar_tick)
    target = tick.history("1y")


    #Index(['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'], dtype='object')

    # normalize target high & low values to percent of opening values
    target['percent_high'] = np.where(target['High'] < 1, target['High'], target['High']/target['Open'])
    target['percent_low']= np.where(target['Low'] < 1, target['Low'], target['Low']/target['Open'])
    target['percent_close']= np.where(target['Close'] < 1, target['Close'], target['Close']/target['Open'])
    # create new columns for 'day of week' and 'week of year'
    target['Date'] = target.index
    target['day_of_week'] = target['Date'].apply(lambda x: x.weekday())
    target['week_num']=target['Date'].dt.isocalendar().week


    # do same as above but for target
    reference['percent_high'] = np.where(reference['High'] < 1, reference['High'], reference['High']/reference['Open'])
    reference['percent_low']= np.where(reference['Low'] < 1, reference['Low'], reference['Low']/reference['Open'])
    reference['percent_close']= np.where(reference['Close'] < 1, reference['Close'], reference['Close']/reference['Open'])
    reference['Date'] = reference.index
    reference['day_of_week'] = reference['Date'].apply(lambda x: x.weekday())
    reference['week_num']=reference['Date'].dt.isocalendar().week
    reference = reference[(reference['Date'].dt.year) != td_year]


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

    diff = np.ones((len(ref_end_i),4))
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

# script to pull data from yfinance

# Import the plotting library
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import numpy as np
import datetime as dt

def foo(arg):


    #algorithm parameters
    years_to_check = 10      # how many years to run analysis over
    trade_days_prior = 10    # how many prior trading days to compare against


    #target and reference dates
    td_year = 2021
    td_month = 2
    td_day = 5
    td_week = dt.date(td_year, td_month, td_day).isocalendar()[1]
    td_day_of_week = dt.date(td_year,td_month,td_day).weekday()


    # Get the data of target stock (AAPL)
    tick = yf.Ticker('AAPL')
    target = tick.history("1y")

    # Get data of reference (DIS - disney)
    tick = yf.Ticker(arg)
    reference = tick.history("15y")


    #Index(['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'], dtype='object')

    # manipulate target & reference to desired format
    target['percent_high'] = np.where(target['High'] < 1, target['High'], target['High']/target['Open'])
    target['percent_low']= np.where(target['Low'] < 1, target['Low'], target['Low']/target['Open'])
    target['percent_close']= np.where(target['Close'] < 1, target['Close'], target['Close']/target['Open'])
    target['Date'] = target.index
    target['day_of_week'] = target['Date'].apply(lambda x: x.weekday())
    target['week_num']=target['Date'].dt.isocalendar().week

    reference['percent_high'] = np.where(reference['High'] < 1, reference['High'], reference['High']/reference['Open'])
    reference['percent_low']= np.where(reference['Low'] < 1, reference['Low'], reference['Low']/reference['Open'])
    reference['percent_close']= np.where(reference['Close'] < 1, reference['Close'], reference['Close']/reference['Open'])
    reference['Date'] = reference.index
    reference['day_of_week'] = reference['Date'].apply(lambda x: x.weekday())
    reference['week_num']=reference['Date'].dt.isocalendar().week


    # find nth day prior to analysis of target
    ref_end_ii = np.where(np.logical_and(reference['day_of_week']==td_day_of_week-1, reference['week_num']==td_week))
    ref_end_i = ref_end_ii[0]

    tar_end_ii = np.where(np.logical_and(target['day_of_week']==td_day_of_week-1, target['week_num']==td_week))
    tar_end_i = tar_end_ii[0]
    tar_start_i = tar_end_i - trade_days_prior

    tar_dat = target.iloc[tar_start_i[0]:tar_end_i[0], :]

    tar_dat_arr_ph = tar_dat['percent_high'].to_numpy()
    tar_dat_arr_pl = tar_dat['percent_low'].to_numpy()
    tar_dat_arr_pc = tar_dat['percent_low'].to_numpy()

    diff = np.ones((len(ref_end_i),3))
    n=0
    for i in ref_end_i:
        ref_start_i = i - trade_days_prior
        ref_dat = reference.iloc[ref_start_i:i, :]
        ref_dat_arr = ref_dat['percent_high'].to_numpy()
        diff[n,0] = sum(abs(ref_dat_arr - tar_dat_arr_ph))
        ref_dat_arr = ref_dat['percent_low'].to_numpy()
        diff[n,1] = sum(abs(ref_dat_arr - tar_dat_arr_pl))
        ref_dat_arr = ref_dat['percent_close'].to_numpy()
        diff[n,2] = sum(abs(ref_dat_arr - tar_dat_arr_pc))
        n=n+1

    return diff
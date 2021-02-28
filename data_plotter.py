import yfinance as yf
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from normalize_tick import normalize_tick


def plot_data(ref_tick, target, target_tick, trade_days_prior, td_year, td_month, td_day, rf_year, diff_min, benchmark):

    # Get day of week & week of year
    td_week = dt.date(td_year, td_month, td_day).isocalendar()[1]
    td_day_of_week = dt.date(td_year,td_month,td_day).weekday()

    # Get the data of target stock
    # TODO have this done before loop is called
    #tick = yf.Ticker(target_tick)
    #target = tick.history("1y")
    #target = normalize_tick(target)
    print(target)
    # Get data of reference
    # TODO put in error handling
    tick = yf.Ticker(ref_tick)
    reference = tick.history(start=dt.datetime(year=int(rf_year-1), month=td_month, day=td_day),
                             end=dt.datetime(year=int(rf_year), month=td_month, day=td_day+5))

    reference = normalize_tick(reference)

    # find nth day prior to analysis of target
    ref_end_ii = np.where(
        np.logical_and(reference['day_of_week'] == td_day_of_week, reference['week_num'] == td_week))

    print(len(ref_end_ii[0]))
    if len(ref_end_ii[0]) > 1:
        ref_end_i = ref_end_ii[0][len(ref_end_ii)]
    else:
        ref_end_i = ref_end_ii[0][0]
    print(ref_end_i)
    ref_start_i = ref_end_i - trade_days_prior - 1

    # Check if the 'prediction day' exists


    tar_end_ii = np.where(np.logical_and(target['day_of_week'] == td_day_of_week - 1, target['week_num'] == td_week))
    tar_end_i = tar_end_ii[0]
    tar_start_i = tar_end_i - trade_days_prior

    tar_dat = target.iloc[tar_start_i[0]:tar_end_i[0], :]

    tar_dat_arr_ph = tar_dat['percent_high'].to_numpy()
    tar_dat_arr_pl = tar_dat['percent_low'].to_numpy()
    tar_dat_arr_pc = tar_dat['percent_close'].to_numpy()

    ref_dat = reference.iloc[ref_start_i:ref_end_i, :]

    ref_dat_arr_ph = ref_dat['percent_high'].to_numpy()
    ref_dat_arr_pl = ref_dat['percent_low'].to_numpy()
    ref_dat_arr_pc = ref_dat['percent_close'].to_numpy()
    predicted_percent_close = ref_dat_arr_pc[len(ref_dat_arr_pc)-1]
    predicted_percent_high = reference['percent_high'].iloc[ref_end_i]

    t1 = list(range(1, int(tar_end_i - tar_start_i+1)))
    t2 = list(range(1, int(ref_end_i - ref_start_i + 1)))

    # REMOVE OR COMMENT OUT IF NOT BENCHMARKING
    t3 = list(range(int(ref_end_i - ref_start_i), int(ref_end_i - ref_start_i + 1)))
    tick = yf.Ticker(target_tick)
    target = tick.history(period='3d', start=dt.datetime(year=int(td_year), month=td_month, day=td_day))
    target['percent_close'] = np.where(target['Close'] < 1, target['Close'], target['Close'] / target['Open'])
    act_dat_arr_pc = np.array([target['percent_close'].iloc[1], target['percent_close'].iloc[0]])

    sendit = np.array([predicted_percent_close, predicted_percent_high])

    if diff_min < 0.04:

        fpath = "./plots/"
        fname = str(td_year)+str(td_month)+str(td_day)+str(target_tick)+'_vs_'+str(ref_tick)+'-'+str(rf_year)

        t1 = list(range(1, int(tar_end_i - tar_start_i + 1)))
        t2 = list(range(1, int(ref_end_i - ref_start_i + 1)))

        # REMOVE OR COMMENT OUT IF NOT BENCHMARKING
        t3 = np.array([int(ref_end_i - ref_start_i -1 ), int(ref_end_i - ref_start_i)])
        tick = yf.Ticker(target_tick)
        target_act = tick.history(period='1d', start=dt.datetime(year=int(td_year), month=td_month, day=td_day))
        target_act['percent_close'] = np.where(target_act['Close'] < 1, target_act['Close'], target_act['Close'] / target_act['Open'])
        act_dat_arr_pc = np.array([tar_dat_arr_pc[len(tar_dat_arr_pc)-1], target_act['percent_close'].iloc[0]])
        plt.clf()
        plt.plot(t1, tar_dat_arr_pc)
        plt.plot(t2, ref_dat_arr_pc)
        plt.plot(t3, act_dat_arr_pc)
        plt.minorticks_on()
        plt.grid(which='major')
        plt.legend([target_tick, ref_tick + ' - ' + str(rf_year), 'actual close'])
        ax = plt.gca()
        ax.set_aspect(50)
        plt.savefig(str(fpath+fname+'.png'))

    return sendit

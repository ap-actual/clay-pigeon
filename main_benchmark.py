from data_pull import get_diff
from data_plotter import plot_data
from pull_ticks import pull_ticks
import datetime as dt
import numpy as np
import progressbar
import yfinance as yf


# Select .dat file to pull ticks from
ref_fname = "./reference.dat"
tar_fname = "./target.dat"

# algorithm parameters
years_to_check = 10  # how many years to pull data from on ticks
trade_days_prior = 7  # how many prior trading days to compare against

benchmark = True

# target and reference dates
td_year = 2021
td_month = 2
td_day = 19

# define weights of analysis (these MUST add up to 1)
w_pl = 0.33
w_ph = 0.33
w_pc = 0.33

# setup progress bar parameters
widgets=[
    ' [', progressbar.Timer(), '] ',
    progressbar.Bar(),
    ' (', progressbar.ETA(), ') ',
]

# import reference ticks & their data from file using custom function
ref_data = pull_ticks(ref_fname)
print(ref_data)

# get size of tick array needed
file = open(ref_fname)
ref_ticks = file.read().split('\n')
file.close()
print(ref_ticks)

# import target ticks from file
file = open(tar_fname)
tar_ticks = file.read().split('\n')
file.close()

# initialize different output, if benchmarking or not
if benchmark:
    test_data = np.zeros((len(tar_ticks), 5))
else:
    test_data = np.zeros((len(tar_ticks), 3))

nn = 0

# run comparison and scoring function for each tick
for tar_tick in progressbar.progressbar(tar_ticks, widgest=widgets):

    # initialize difference array (low diff = high score)
    diff = np.zeros((10, 6, len(ref_ticks)))

    # compute similarity to each ref tick and store differences
    n = 0  # loop counter
    for reference in ref_data:
        try:
            x = get_diff(ref_data[reference], tar_tick, trade_days_prior, td_year, td_month, td_day)  # call get_diff
            diff[0:len(x[:, 1:]), 0:4, n] = x  # find size of variable, and cast into diff array

            # apply weights to differences, create new column with score
            diff[0:len(x[:, 1:]), 4, n] = \
                diff[0:len(x[:, 1:]), 1, n]*w_ph + diff[0:len(x[:, 2:]), 3, n]*w_pl + diff[0:len(x[:, 1:]), 3, n]*w_pc
            n = n + 1
        except:
            n = n + 1
            pass

    # Find absolute minimum and row of minimum
    masked_diff = np.ma.masked_equal(diff[:, 4, :], 0.0, copy=False)
    diff_min = np.amin(masked_diff)
    diff_imin = np.where(masked_diff == np.amin(masked_diff))

    print('Most similar stock: ')
    print(ref_ticks[diff_imin[1][0]])
    print(diff[diff_imin[0][0], 0, diff_imin[1][0]]) # reference diff[min year, year col, diff stock tick]
    print('Similarity:')
    print(diff_min)

    gainz = plot_data(ref_ticks[diff_imin[1][0]], tar_tick, trade_days_prior,
              td_year, td_month, td_day, diff[diff_imin[0][0], 0, diff_imin[1][0]], diff_min)

    tick = yf.Ticker(tar_tick)
    target = tick.history(period='1d', start=dt.datetime(year=int(td_year), month=td_month, day=td_day))
    target['percent_close'] = np.where(target['Close'] < 1, target['Close'], target['Close'] / target['Open'])
    target['percent_high'] = np.where(target['High'] < 1, target['High'], target['High'] / target['Open'])
    print('predicted gains = ' + str(gainz[0]))
    print('actual gains = ' + str(target['percent_close'].iloc[0]))
    test_data[nn, 0] = gainz[0]
    test_data[nn, 1] = target['percent_close'].iloc[0]
    test_data[nn, 2] = diff_min
    test_data[nn, 3] = gainz[1]
    test_data[nn, 4] = target['percent_high'].iloc[0]
    nn = nn + 1

np.savetxt("plots/test_data.txt", test_data, header='Predicted Close Return, Actual Close Return, '
                                              'Confidence, Predicted Day-High Return, Actual Day-High Return')

from data_pull import get_diff
from data_plotter import plot_data
import datetime as dt
import numpy as np
import progressbar
import yfinance as yf

# setup progress bar parameters
widgets=[
    ' [', progressbar.Timer(), '] ',
    progressbar.Bar(),
    ' (', progressbar.ETA(), ') ',
]

# algorithm parameters
years_to_check = 10  # how many years to run analysis over
trade_days_prior = 7  # how many prior trading days to compare against

# target and reference dates
td_year = 2021
td_month = 2
td_day = 5


# define weights of analysis (these MUST add up to 1)
w_pl = 0.33
w_ph = 0.33
w_pc = 0.34

# import reference ticks from file
file = open("./reference.dat")
ref_ticks = file.read().split('\n')
file.close()
print(ref_ticks)

# import target ticks from file
file = open("./target.dat")
tar_ticks = file.read().split('\n')
file.close()

test_data = np.zeros((len(tar_ticks), 3))
nn = 0




# TODO change this to use file targets
for tar_tick in progressbar.progressbar(tar_ticks, widgest=widgets):

    # initialize difference array
    diff = np.zeros((10, 6, len(ref_ticks)))

    # loop through reference ticks
    n = 0  # loop counter
    for ref_tick in ref_ticks:
        try:
            x = get_diff(ref_tick, tar_tick, trade_days_prior, td_year, td_month, td_day)  # call get_diff from data_pull.py & cast into variable
            diff[0:len(x[:, 1:]), 0:4, n] = x  # find size of variable, and cast into diff array
            diff[0:len(x[:, 1:]), 4, n] = diff[0:len(x[:, 1:]), 1, n]*w_ph + diff[0:len(x[:, 2:]), 3, n]*w_pl + diff[0:len(x[:, 1:]), 3, n]*w_pc  # apply weights to differences, create new column with score
            n = n + 1
        except:
            n = n + 1
            pass

    # Find absolute minimum and location of minimum
    masked_diff = np.ma.masked_equal(diff[:, 4, :], 0.0, copy=False)
    diff_min = np.amin(masked_diff)
    diff_imin = np.where(masked_diff == np.amin(masked_diff))

    print('Most similar stock: ')
    print(ref_ticks[diff_imin[1][0]])
    print(diff[diff_imin[0][0], 0, diff_imin[1][0]]) # reference diff[min year, year col, diff stock tick]
    print('Similarity:')
    print(diff_min)

    gainz = plot_data(ref_ticks[diff_imin[1][0]], tar_tick, trade_days_prior,
              td_year, td_month, td_day, diff[diff_imin[0][0], 0, diff_imin[1][0]])

    tick = yf.Ticker(tar_tick)
    target = tick.history(period='1d', start=dt.datetime(year=int(td_year), month=td_month, day=td_day))
    target['percent_close'] = np.where(target['Close'] < 1, target['Close'], target['Close'] / target['Open'])
    print('predicted gains = ' + str(gainz))
    print('actual gains = ' + str(target['percent_close'].iloc[0]))
    test_data[nn,0] = gainz
    test_data[nn,1] = target['percent_close'].iloc[0]
    test_data[nn,2] = diff_min
    nn = nn + 1
    print(test_data)

np.savetxt("test_data.csv", test_data, delimeter=",")
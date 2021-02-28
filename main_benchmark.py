from data_pull import get_diff
from pull_ticks import pull_ticks
import numpy as np
import progressbar
import yfinance as yf
from normalize_tick import normalize_tick
from get_prediction import get_prediction


# Select .dat file to pull ticks from
ref_fname = "./reference.dat"
tar_fname = "./target.dat"
log_fname = "plots/log.txt"

# open log file
fid = open(log_fname, "w")

# algorithm parameters
years_to_check = 10  # how many years to pull data from on ticks
trade_days_prior = 7  # how many prior trading days to compare against

benchmark = True

# target and reference dates
td_year = 2021
td_month = 2
td_day = 24

# define weights of analysis (these MUST add up to 1)
w_pl = 0.33
w_ph = 0.33
w_pc = 0.33

# setup progress bar parameters
widgets = [
    ' [', progressbar.Timer(), '] ',
    progressbar.Bar(),
    ' (', progressbar.ETA(), ') ',
]

# import reference ticks & their data from file using custom function
ref_data = pull_ticks(ref_fname)

# get size of tick array needed
file = open(ref_fname)
ref_ticks = file.read().split('\n')
file.close()

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

    # Get the data of target stock
    tick = yf.Ticker(tar_tick)
    target = tick.history("1y")
    target = normalize_tick(target)

    # compute similarity to each ref tick and store differences
    n = 0  # loop counter
    for reference in ref_data:
        try:
            x = get_diff(ref_data[reference], target, trade_days_prior, td_year, td_month, td_day)  # call get_diff
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

    # ref tick string = ref_ticks[diff_imin[1][0]]

    try:
        gainz = get_prediction(ref_data[reference], td_year, td_month, td_day,
                               diff[diff_imin[0][0], 0, diff_imin[1][0]], benchmark)
    except:
        gainz = np.array([0, 0])
        fid.write('ERROR PULLING PREDICTION')


    test_data[nn, 0] = gainz[0]
    test_data[nn, 1] = target['percent_close'].iloc[0]
    test_data[nn, 2] = diff_min
    test_data[nn, 3] = gainz[1]
    test_data[nn, 4] = target['percent_high'].iloc[0]

    fid.write('\n====================================================\n')
    fid.write('Target Stock: ')
    fid.write(tar_tick)
    fid.write('\nMost similar stock: ')
    fid.write(str(ref_ticks[diff_imin[1][0]]))
    fid.write(' year ')
    fid.write(str(diff[diff_imin[0][0], 0, diff_imin[1][0]]))
    fid.write('\nSimilarity: ')
    fid.write(str(diff_min))
    nn = nn + 1

fid.close()
np.savetxt("plots/test_data.txt", test_data, header='Predicted Close Return, Actual Close Return, '
                                              'Confidence, Predicted Day-High Return, Actual Day-High Return',
           delimiter=',')
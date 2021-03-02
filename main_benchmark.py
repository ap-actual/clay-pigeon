from data_pull import get_diff
from pull_ticks import pull_ticks
import numpy as np
import progressbar
import yfinance as yf
from normalize_tick import normalize_tick
from get_prediction import get_prediction
import datetime as dt


# define weights of analysis (these MUST add up to 1)
w_pl = 0.33
w_ph = 0.33
w_pc = 0.33

# target and reference dates
td_year = 2021
td_month = 2
td_day = 24

# Select .dat file to pull ticks from
ref_fname = "./reference_short.dat"
tar_fname = "./target_short.dat"
log_fname = "plots/log.txt"
dat_fame = "plots/dat.csv"

# open log & data file
fid = open(log_fname, "w")
fid2 = open(dat_fame, "w")

fid2.write('Target Tick, Reference Tick, Confidence, Predicted Close Return, '
           'Actual Close Return,  Predicted Day-High Return, Actual Day-High Return, roi, score')

# algorithm parameters
trade_days_prior = 7  # how many prior trading days to compare against

benchmark = True

# day of week data
td_week = dt.date(td_year, td_month, td_day).isocalendar()[1]
td_day_of_week = dt.date(td_year, td_month, td_day).weekday()

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

score = np.zeros((len(tar_ticks)))
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

    try:
        gainz = get_prediction(ref_data[ref_ticks[diff_imin[1][0]]], td_year, td_month, td_day,
                               diff[diff_imin[0][0], 0, diff_imin[1][0]], benchmark)
    except:
        gainz = np.array([0, 0])
        fid.write('ERROR PULLING PREDICTION')


    fid.write('\n====================================================\n')
    fid.write('Target Stock: ')
    fid.write(tar_tick)
    fid.write('\nMost similar stock: ')
    fid.write(str(ref_ticks[diff_imin[1][0]]))
    fid.write(' year ')
    fid.write(str(diff[diff_imin[0][0], 0, diff_imin[1][0]]))
    fid.write('\nSimilarity: ')
    fid.write(str(diff_min))

    fid2.write('\n')
    fid2.write(str(tar_tick))
    fid2.write(',')
    fid2.write(str(ref_ticks[diff_imin[1][0]]))
    fid2.write(',')
    fid2.write(str(diff_min))
    fid2.write(',')
    fid2.write(str(gainz[0]))
    fid2.write(',')
    tar_end_ii = np.where(np.logical_and(target['day_of_week'] == td_day_of_week - 1, target['week_num'] == td_week))
    tar_end_i = tar_end_ii[0]
    actual_close = target['percent_close'].iloc[tar_end_i].to_numpy()
    fid2.write(str(actual_close[0]))
    fid2.write(',')
    fid2.write(str(gainz[1]))
    fid2.write(',')
    actual_high = target['percent_high'].iloc[tar_end_i].to_numpy()
    fid2.write(str(actual_high[0]))

    if(gainz[1] < target['percent_high'].iloc[tar_end_i].to_numpy()):
        roi = gainz[1]
    else:
        roi = target['percent_close'].iloc[tar_end_i].to_numpy()

    # compute score of weights
    score[nn] = (1/(1-diff_min)) * (roi - 1)

    fid2.write(',')
    fid2.write(str(roi))
    fid2.write(',')
    fid2.write(str(score[nn]))

    nn = nn + 1

fid.close()
fid2.close()

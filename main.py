from data_pull import get_diff
import numpy as np
from progressbar import ProgressBar

prgbar = ProgressBar()  # initialize progress bar

# define weights of analysis (these MUST add up to 1
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
print(tar_ticks)


diff = np.zeros((15, 6, len(ref_ticks)))  # initialize difference array

n = 0  # loop counter
for tick in prgbar(ref_ticks):
    x = get_diff(tick)  # call get_diff from data_pull.py & cast into variable
    diff[0:len(x[:, 1:]), 0:4, n] = x  # find size of variable, and cast into diff array
    diff[0:len(x[:, 1:]), 4, n] = diff[0:len(x[:, 1:]), 1, n]*w_ph + diff[0:len(x[:, 2:]), 3, n]*w_pl + diff[0:len(x[:, 1:]), 3, n]*w_pc  # apply weights to differences, create new column with score
    n = n+1
print(diff[:, 1:5, n-1])
masked_diff = np.ma.masked_equal(diff[:,4,:], 0.0, copy=False)
print(np.amin(masked_diff))
print(np.where(masked_diff == np.amin(masked_diff)))
print(diff[7, 4, 4])
print(diff[7,0,4])

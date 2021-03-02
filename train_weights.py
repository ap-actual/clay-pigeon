from main_benchmark_fun import benchmark_fun
from pull_ticks import pull_ticks
import numpy as np

w_pl = 0.0

td_year = 2021
td_month = 2
td_day = 25

ref_fname = "./reference.dat"
tar_fname = "./target.dat"

fid3 = open("results.csv", "w")

ref_data = pull_ticks(ref_fname)

w_pc_arr = np.linspace(0, 1, num=11)
w_ph_arr = np.linspace(1, 0, num=11)

score = np.zeros((len(w_pc_arr), len(w_ph_arr)))

i = 0
j = 0
for w_pc in w_ph_arr:
    for w_ph in w_ph_arr:


        score[i,j] = benchmark_fun(w_pl, w_ph, w_pc, td_year, td_month, td_day, ref_data, ref_fname, tar_fname)
        fid3.write(score[i, j])
        fid3.write(",")
        print(score)
        i = i+1
    fid3.write("\n")
    j = j+1
fid3.close()

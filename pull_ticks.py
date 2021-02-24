from data_pull import get_diff
from data_plotter import plot_data
import datetime as dt
import numpy as np
import progressbar
import yfinance as yf


def pull_ticks(fname):
    # setup progress bar parameters
    widgets=[
        ' [', progressbar.Timer(), '] ',
        progressbar.Bar(),
        ' (', progressbar.ETA(), ') ',
    ]

    file = open(fname)
    ref_ticks = file.read().split('\n')
    file.close()
    print(ref_ticks)

    ref_collection = {}

    print("pulling reference ticks...")
    for ref_tick in progressbar.progressbar(ref_ticks, widgest=widgets):

        tick = yf.Ticker(ref_tick)
        reference = tick.history("15y")
        ref_collection[ref_tick] = reference

    return ref_collection

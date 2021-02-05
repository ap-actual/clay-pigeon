from data_pull import foo
from numpy import loadtxt
import numpy as np

lines = []

file = open("./reference.dat")
lines = file.read().split('\n')
file.close()
print(lines)

diff = np.zeros((15, 3, len(lines)))
n = 0
for tick in lines:
    x = foo(tick)
    diff[0:len(x[:,0]), :, n] = x
    n=n+1
    print(n)
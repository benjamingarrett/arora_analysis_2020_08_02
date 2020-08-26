# Usage: <csv_file>
# Assumes the csv contains two columns: cache_size,cache_misses
# Looking to discover the relationship here and confirm a conjecture
# in a separate script


import os, sys, matplotlib.pyplot as plt
from math import sqrt, log
import numpy as np
from scipy import stats
from sklearn.metrics import r2_score


def get_list(fn):
  print('fn {}'.format(fn))
  return [ln.rstrip('\n').split(',') for ln in open(fn)]


def get_sort_by(fn):
  print('fn {}'.format(fn))
  lst = [ln.rstrip('\n').split(',') for ln in open(fn)]
  j = 0
  while j < len(lst):
    if lst[j][0] == 'SORT_BY':
      return int(lst[j][1])
    j += 1
  print('SORT_BY field not found in {}/{}'.format(fn))
  exit()


def get_comment(fn):
  print('fn {}'.format(fn))
  lst = [ln.rstrip('\n').split(',') for ln in open(fn)]
  j = 0
  while j < len(lst):
    if lst[j][0] == 'COMMENT':
      return lst[j][1]
    j += 1
  print('COMMENT field not found in {}/{}'.format(fn))
  exit()


def points_from_csv_with_n(fname, col=1, rows_to_skip=0):
  print('fn {}'.format(fname))
  n = get_sort_by(fname)
  name = get_comment(fname)
  lst = get_list(fname)[rows_to_skip:]
  return n, name, [(int(k[0]), int(k[col])) for k in lst]


def semilogx_regression(x, y, basex=2):
  lgx = [log(k, basex) for k in x]
  m, b, r, p, err = stats.linregress(lgx, y)
  return m, b, r


print('args: {}'.format(sys.argv))
if len(sys.argv) < 2:
  print('Usage: <csv_file>')
  exit()
fn = sys.argv[1]
point_sequence = {}
n, name, lst = points_from_csv_with_n(fn, rows_to_skip=2)
print('n {}  lst {}'.format(n, lst))
point_sequence[(n, fn, name)] = lst
minx = 8
maxx = 1024
x = [k[0] for k in lst if minx <= k[0] and k[0] <= maxx]
y = [k[1] for k in lst if minx <= k[0] and k[0] <= maxx]
m, b, r = semilogx_regression(x, y)
regression_pts_x = np.linspace(minx, maxx, 1000)
regress_func = lambda x: b + log(x, 2) * m


fig = plt.figure()
ax = fig.add_subplot(111)

#plt.semilogx([k[0] for k in lst], [k[1] for k in lst], '*', basex=2, label='{}'.format(name))
#plt.semilogx([k for k in regression_pts_x], [regress_func(k) for k in regression_pts_x], basex=2, label='regression fit, r={}'.format(r))

ax.plot([k[0] for k in lst], [k[1] for k in lst], '*', label='{}'.format(name))
ax.plot([k for k in regression_pts_x], [regress_func(k) for k in regression_pts_x], label='regression fit, r={}'.format(r))

plt.xlabel('cache size')
plt.ylabel('cache misses')
t = 'Arora, LRU'
ax.legend(loc='upper right')
plt.title(t)
plt.show()

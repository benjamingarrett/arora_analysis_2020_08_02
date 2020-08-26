# Usage: <folder>
# Assumes: csize,misses
# Each csv contains two rows: COMMENTS & SORT_BY
# Investigating KMP FF


import os, sys, matplotlib.pyplot as plt
from math import sqrt
import numpy as np
from scipy import stats
from sklearn.metrics import r2_score


def get_list(dr, fn):
  print('fn {}'.format(fn))
  return [ln.rstrip('\n').split(',') for ln in open(dr+'/'+fn)]


def get_sort_by(dr, fn):
  print('fn {}'.format(fn))
  lst = [ln.rstrip('\n').split(',') for ln in open(dr+'/'+fn)]
  j = 0
  while j < len(lst):
    if lst[j][0] == 'SORT_BY':
      return int(lst[j][1])
    j += 1
  print('SORT_BY field not found in {}/{}'.format(dr, fn))
  exit()


def get_comment(dr, fn):
  print('fn {}'.format(fn))
  lst = [ln.rstrip('\n').split(',') for ln in open(dr+'/'+fn)]
  j = 0
  while j < len(lst):
    if lst[j][0] == 'COMMENT':
      return lst[j][1]
    j += 1
  print('COMMENT field not found in {}/{}'.format(dr, fn))
  exit()


def points_from_csv_with_n(dr, fname, col=1, rows_to_skip=0):
  print('fn {}'.format(fname))
  n = get_sort_by(dr, fname)
  name = get_comment(dr, fname)
  lst = get_list(dr, fname)[rows_to_skip:]
  return n, name, [(int(k[0]), int(k[col])) for k in lst]



print('args: {}'.format(sys.argv))
if len(sys.argv) < 2:
  print('Usage: <folder>')
  exit()
folder = sys.argv[1]
fnames = [fn for fn in os.listdir(folder) if 'csv' in fn]
point_sequences = {}
for fn in fnames:
  n, name, lst = points_from_csv_with_n(folder, fn, rows_to_skip=2)
  print('n {}  lst {}'.format(n, lst))
  point_sequences[(n, fn, name)] = lst





fig = plt.figure()
ax = fig.add_subplot(111)
for tup, seq in point_sequences.items():
  minx = min([k[0] for k in seq])
  maxx = max([k[0] for k in seq])
  lower_bound = lambda x: n**2 / (2*x)
  upper_bound = lambda x: n**2 / (2*x) + n*sqrt(n)/x
  poly_pts_x = np.linspace(minx, maxx, 1000)
  ax.plot([k[0] for k in seq], [k[1] for k in seq], '*', label='{}'.format(tup[2]))
  ax.plot([k for k in poly_pts_x], [lower_bound(k) for k in poly_pts_x], label='lower bound')
  ax.plot([k for k in poly_pts_x], [upper_bound(k) for k in poly_pts_x], label='upper_bound')
plt.xlabel('cache size')
plt.ylabel('cache misses')
t = 'Arora, LRU'
ax.legend(loc='upper right')
plt.title(t)
plt.show()

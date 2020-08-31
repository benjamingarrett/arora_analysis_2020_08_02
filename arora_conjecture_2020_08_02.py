# Usage: <csv_file>
# Assumes the csv contains two columns: cache_size,cache_misses
# Each csv contains two rows: COMMENTS & SORT_BY
# Investigating Arora with LRU


import os, sys, matplotlib.pyplot as plt
from math import sqrt, log
import numpy as np
from scipy import stats
from sklearn.metrics import r2_score


MAX_ITERATIONS = 1000000

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
  print('SORT_BY field not found in {}'.format(fn))
  exit()


def get_comment(fn):
  print('fn {}'.format(fn))
  lst = [ln.rstrip('\n').split(',') for ln in open(fn)]
  j = 0
  while j < len(lst):
    if lst[j][0] == 'COMMENT':
      return lst[j][1]
    j += 1
  print('COMMENT field not found in {}'.format(fn))
  exit()


def points_from_csv_with_n(fname, col=1, rows_to_skip=0):
  print('fn {}'.format(fname))
  n = get_sort_by(fname)
  name = get_comment(fname)
  lst = get_list(fname)[rows_to_skip:]
  return n, name, [(int(k[0]), int(k[col])) for k in lst]


def semilogx_regression(pts, minx, maxx, basex=2):
  lgx = [log(k[0], basex) for k in pts if minx <= k[0] and k[0] <= maxx]
  y = [k[1] for k in pts if minx <= k[0] and k[0] <= maxx]
  m, b, r, p, err = stats.linregress(lgx, y)
  return m, b, r


def running_max(pts, minx, maxx):
  filtered_pts = sorted([k for k in pts if minx <= k[0] and k[0] <= maxx], key=lambda k: k[1])
  j = 0
  while j < len(filtered_pts):
    print('{} -- {}'.format(filtered_pts[j][0], filtered_pts[j][1]))
    j += 1
  maxx = [filtered_pts[0][0]]
  maxy = [filtered_pts[0][1]]
  j = 0
  while j < len(filtered_pts):
    maxx.insert(0, filtered_pts[j][0])
    if filtered_pts[j][1] > maxy[0]:
      maxy.insert(0, filtered_pts[j][1])
    else:
      maxy.insert(0, maxy[0])
    j += 1
  return list(zip(maxx, maxy))


def right_endpoints(pts, minx, maxx):
  filtered_pts = sorted([k for k in pts if minx <= k[0] and k[0] <= maxx], key=lambda k: k[1])
  j = 0
  rightx = [filtered_pts[0][0]]
  righty = [filtered_pts[0][1]]
  while j < len(filtered_pts):
    if filtered_pts[j][1] > righty[0]:
      rightx.insert(0, filtered_pts[j][0])
      righty.insert(0, filtered_pts[j][1])
    j += 1
  return list(zip(rightx, righty))


def bounds_above(pts, f, minx, maxx):
  j = 0
  while j < len(pts):
    if minx <= pts[j][0] and pts[j][0] <= maxx:
      if float(pts[j][1]) >= float(f(pts[j][0])):
        return False
    j += 1
  return True


def bounds_below(pts, f, minx, maxx):
  j = 0
  while j < len(pts):
    if minx <= pts[j][0] and pts[j][0] <= maxx:
      if float(pts[j][1]) <= float(f(pts[j][0])):
        return False
    j += 1
  return True


def find_upper_bound_1(pts, m, b, minx, maxx, eps=0.0001):
  lo_b = b
  print('expansion starting at {}'.format(lo_b))
  f = lambda x: b + log(x, 2) * m
  cnt = 0
  while not bounds_above(pts, f, minx, maxx):
    if cnt > MAX_ITERATIONS:
      print('did not find an upper bound')
      exit()
    cnt += 1
    b *= 2
  hi_b = b
  print('expansion stopped at b = {}'.format(hi_b))
  print('search interval = {}'.format(hi_b - lo_b))
  search_interval = float(hi_b - lo_b)
  while search_interval > eps:
    b = lo_b + float(hi_b - lo_b) / 2.0
    if bounds_above(pts, f, minx, maxx):
      print('too high')
      hi_b = b
    else:
      print('too low')
      lo_b = b
    search_interval = float(hi_b - lo_b)
    print('{} -- {} -- {}'.format(lo_b, hi_b, search_interval))
  return m, b


def find_upper_bound_2(pts, m, b, minx, maxx, eps=0.0001):
  lo_m = m
  print('expansion starting at {}'.format(lo_m))
  f = lambda x: b + log(x, 2) * m
  cnt = 0
  while not bounds_above(pts, f, minx, maxx):
    if cnt > MAX_ITERATIONS:
      print('expansion did not stop')
      exit()
    cnt += 1
    m += 1
  hi_m = m
  print('expansion stopped at m = {}'.format(hi_m))
  print('search interval = {}'.format(hi_m - lo_m))
  search_interval = float(hi_m - lo_m)
  while search_interval > eps:
    m = lo_m + float(hi_m - lo_m) / 2.0
    if bounds_above(pts, f, minx, maxx):
      print('too high')
      hi_m = m
    else:
      print('too low')
      lo_m = m
    search_interval = float(hi_m - lo_m)
    print('{} -- {} -- {}'.format(lo_m, hi_m, search_interval))
  return m, b



def find_lower_bound_exponential_from_semilogx_regression_coefficients(pts, m, b, minx, maxx):
  pass


print('args: {}'.format(sys.argv))
if len(sys.argv) < 2:
  print('Usage: <csv_file>')
  exit()
fn = sys.argv[1]
point_sequence = {}
n, name, original_pts = points_from_csv_with_n(fn, rows_to_skip=2)
minx = 8
maxx = 1024
running_max_pts = running_max(original_pts, minx, maxx)
right_endpoints_pts = right_endpoints(original_pts, minx, maxx)

m, b, r = semilogx_regression(right_endpoints_pts, minx, maxx)
regression_pts_x = np.linspace(minx, maxx, 1000)
regress_func = lambda x: b + log(x, 2) * m


m_up_1, b_up_1 = find_upper_bound_1(right_endpoints_pts, m, b, minx, maxx)
upper_func_1 = lambda x: b_up_1 + log(x, 2) * m_up_1
r2_value_1 = r2_score([k[1] for k in right_endpoints_pts], [upper_func_1(k[0]) for k in right_endpoints_pts])

m_up_2, b_up_2 = find_upper_bound_2(right_endpoints_pts, m, b, minx, maxx)
upper_func_2 = lambda x: b_up_2 + log(x, 2) * m_up_2
r2_value_2 = r2_score([k[1] for k in right_endpoints_pts], [upper_func_2(k[0]) for k in right_endpoints_pts])



fig = plt.figure()
ax = fig.add_subplot(111)

'''
plt.semilogx([k[0] for k in lst], [k[1] for k in lst], '*', basex=2, label='{}'.format(name))
plt.semilogx([k for k in regression_pts_x], [regress_func(k) for k in regression_pts_x], basex=2, label='regression fit, r={}'.format(r))
'''

ax.plot([k[0] for k in original_pts], [k[1] for k in original_pts], '*', label='{}'.format(name))
ax.plot([k[0] for k in running_max_pts], [k[1] for k in running_max_pts], '*', label='running max')
ax.plot([k[0] for k in right_endpoints_pts], [k[1] for k in right_endpoints_pts], '*', label='right endpoints')
ax.plot([k for k in regression_pts_x], [regress_func(k) for k in regression_pts_x], label='regression fit, b={}, m={}, r={}'.format(b, m, r))
ax.plot([k for k in regression_pts_x], [upper_func_1(k) for k in regression_pts_x], label='upper bound 1, b={}, m={}, r={}'.format(b_up_1, m_up_1, r2_value_1))
ax.plot([k for k in regression_pts_x], [upper_func_2(k) for k in regression_pts_x], label='upper bound 2, b={}, m={}, r={}'.format(b_up_2, m_up_2, r2_value_2))

plt.xlabel('cache size')
plt.ylabel('cache misses')
t = 'Arora, LRU, bound function: f(x) = b + log_2(x) * m'
ax.legend(loc='upper right')
plt.title(t)
plt.show()


#!/usr/bin/env python2
# coding: utf-8
#
#   Author: Xiang Wang (xiang.wang.s@gmail.com)
#
#   Organization: Network Security Laboratory (NSLab),
#                 Research Institute of Information Technology (RIIT),
#                 Tsinghua University (THU)
#

import pc
import sys

from copy import deepcopy
from policyspace import HyperRect, PolicySpace


rs = pc.load_rules(sys.argv[1])

print('Test 1')
def_n = PolicySpace([HyperRect(deepcopy(rs[-1][:5]))])
for r in rs[:-1]:
    def_n.sub_rect(HyperRect(r[:5]))

def_r = PolicySpace([HyperRect(deepcopy(rs[-1][:5]))])
for r in reversed(rs[:-1]):
    def_r.sub_rect(HyperRect(r[:5]))

print(len(def_n.rects), len(def_r.rects))
assert def_n == def_r
assert not def_n - def_r

print('Test 2')
eff_n = PolicySpace([HyperRect(deepcopy(rs[0][:5]))])
for r in rs[1:-1]:
    eff_n.or_rect(HyperRect(r[:5]))

eff_r = PolicySpace([HyperRect(deepcopy(rs[-2][:5]))])
for r in reversed(rs[:-2]):
    eff_r.or_rect(HyperRect(r[:5]))

print(len(eff_n.rects), len(eff_r.rects))
assert eff_n == eff_r
assert not eff_n - eff_r

print('Test 3')
overall = PolicySpace([HyperRect(deepcopy(rs[-1][:5]))])

assert eff_n | def_r == overall
assert not eff_r & def_n
assert eff_n & eff_r == eff_n
assert def_n & def_r == def_n
assert def_n - eff_n == def_r
assert eff_r - def_r == eff_n


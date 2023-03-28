#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-03-12 16:18:44
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-19 12:37:16
"""

from MADBuf import *
from RegressionTest.FetchExample import *
from RegressionTest.Experiments import *
from subprocess import run
import art

import sys

if __name__ == "__main__":

    art.tprint("MADBuf")

    param = Params()
    param.max_expansion_level = 0
    param.add_cutloopback_constraints_flag = True
    param.add_blockbox_constraints_flag = True
    param.add_blackbox_delay_propagation_flag = False
    param.cutless_hueristic = 4
    param.timeout = 60

    experiment = Experiment(param)

    experiment()

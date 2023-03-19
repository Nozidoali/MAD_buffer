#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-19 00:09:28
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-19 00:09:50
'''

import gurobipy as gp
from gurobipy import GRB
from MADBuf.Network.BLIFGraph import *
from MADBuf.Utils import *


def add_input_delay_constraints(
    model: gp.Model, g: BLIFGraph, input_delays: dict = None
):

    if input_delays != None:
        """
        we will allow users to specify the input delays (arrival times at the module inputs)
        """
        return NotImplementedError

    else:
        """
        By default we assume all input delays = 0
        """
        for input_signal in g.inputs.union(g.ros):

            input_var = model.getVarByName(f"TimingLabel_{input_signal}")

            model.addConstr(input_var == 0, f"InputDelay_{input_signal}")

    model.update()
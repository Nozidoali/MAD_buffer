#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-19 00:35:02
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-19 00:38:31
'''

import gurobipy as gp
from MADBuf.Utils import *

def run_gurobi_optimization(model: gp.Model, **kwargs) -> gp.Model:

    verbose = get_value_from_kwargs(kwargs, 'verbose', False)

    if verbose:
        model.Params.OutputFlag = 1
    else:
        model.Params.OutputFlag = 0

    time_limit = get_value_from_kwargs(kwargs, 'time_limit', 3600)

    # now we solve the model under the time limit
    #
    model.Params.timeLimit = time_limit

    if verbose:
        print_orange("Solving the model...")
    model.optimize()
    
    if verbose:
        print_blue(f"Model status: {model.status}")

    if model.status == gp.GRB.INFEASIBLE or model.status == gp.GRB.INF_OR_UNBD:
        print_red("Infeasible model")
        model.computeIIS()
        return
    
    if model.status == gp.GRB.TIME_LIMIT:
        print_red("Time limit reached")
    
    if model.status == gp.GRB.OPTIMAL:
        print_green("Optimal solution found")

    if model.status == gp.GRB.UNBOUNDED:
        print_red("Unbounded model")
        return
    
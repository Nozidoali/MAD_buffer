#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-21 13:20:46
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-21 13:36:18
'''

from MADBuf import *
from FetchExample.EvaluateMadbuf import *
from FetchExample.EvaluateMilp import *
from FetchExample.EvaluateCycles import *

def submit_solution(*args, **kwargs):


    if "method" not in kwargs:
        raise Exception("method is not specified")

    method = kwargs["method"]
    print_blue(f"Running {method}...")

    if "mut" not in kwargs:
        raise Exception("Please provide the module under test name")

    mut = kwargs["mut"]
    print_blue(f"Module under test: {mut}")

    print_blue(f"\n\n[i] Submit Solution for {mut} using {method}... ")

    for key, value in kwargs.items():
        print(f"{key}: {text_orange(value)}")
    
    if method == "madbuf":
        evaluate_madbuf(**kwargs)

    elif method == "milp":
        evaluate_milp(**kwargs)

    # before running simulation, we need to check the correctness of the solution
    dfg_ref = read_dfg(f"./{mut}/reports/{mut}.dot")
    dfg = read_dfg(f"./{mut}/reports/{mut}_{method}.dot")
    
    print_blue("\n\n[i] Checking equivalence...", end=' ', flush=True)
    assert equivalence_checking(dfg_ref, dfg)
    print_green("PASS")

    cycles = evaluate_num_cycles(**kwargs)

    run_synthesis = get_value_from_kwargs(
        kwargs, ["run_synthesis", "run_optimization"], False
    )

    # evaluate delay
    # we get the delay in ns, and the number of FFs, and the number of LUTs
    values = evaluate_delay(dfg, mut, run_synthesis=run_synthesis)

    return cycles, values

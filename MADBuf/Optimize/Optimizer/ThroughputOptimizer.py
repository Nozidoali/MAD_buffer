#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-18 21:50:41
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-19 00:40:33
'''

from Optimize import OptimizerBase
from MADBuf.Utils import *
from MADBuf.Optimize.Constructor import *
from MADBuf.Optimize.Constraints import *
from MADBuf.Optimize.Variables import *
from MADBuf.Optimize.ModelUtils import *
from MADBuf.Optimize.Solver import *

class ThroughputOptimizer(OptimizerBase):

    def __init__(self, *args, **kwargs) -> None:
        
        super().__init__(*args, **kwargs)

        self.clock_period: int
        self.lps: list
        self.model: gp.Model
        
        self.signal_to_variable: dict

        self.parse_clock_period(*args, **kwargs)
        self.parse_lps(*args, **kwargs)

    def run_optimization(self, *args, **kwargs):
        self.build_model(*args, **kwargs)
        run_gurobi_optimization(*args, **kwargs)

    def get_solution(self, *args, **kwargs):
        buffers = retrieve_buffers(self.model)
        buffer_slots = retrieve_buffers_to_n_slots(self.model)
        signal_to_cut = retrieve_cuts(self.model, self.signal_to_cuts)
        signal_to_label = retrieve_timing_labels(self.model)

        dfg = self.dfg.copy()
        insert_buffers_in_dfg(dfg, buffers, buffer_slots, verbose=True)
        return dfg

    
    def parse_clock_period(self, *args, **kwargs):
        
        # get the target clock period, if not specified, raise an exception
        clock_period: int = get_value_from_kwargs(kwargs, [
            'clock_period',
            'cp'
        ], None)

        if clock_period is None:
            raise Exception('Clock period is not specified')
        
        self.clock_period = clock_period

    def parse_lps(self, *args, **kwargs):
        
        # get the LPs to be optimized, if not specified, raise an exception
        lps: list = get_value_from_kwargs(kwargs, [
            'lps',
            'lp',
            'dynamatic_lps',
        ], None)
        if lps is None:
            raise Exception('LPs are not specified')
        
        self.lps = lps

        model = load_model(self.lps, verbose=self.verbose)
        remove_timing_constraints(model)

        self.model = model

        self.signal_to_variable = get_signal_to_variable(
            model,
            signal_to_channel=self.signal_to_channel,
            dfg_mapped=self.dfg_mapped,
            mapping=self.mapping,
        )

    def build_model(self, *args, **kwargs):

        cut_loopback = get_value_from_kwargs(kwargs, [
            'cut_loopback',
            'add_cutloopback_constraints_flag'
        ], False)
        
        blackbox = get_value_from_kwargs(kwargs, [
            'blackbox',
            'add_cutloopback_constraints_flag'
        ], False)

        add_timing_constraints(
            self.model,
            self.network,
            self.signal_to_cuts,
            self.signal_to_channel,
            self.mappings,
            add_cutloopback_constraints_flag=cut_loopback,
            add_blockbox_constraints_flag=blackbox,
            clock_period=self.clock_period,
            verbose=True,
        )
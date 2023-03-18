#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-18 21:56:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-19 00:00:38
'''

from MADBuf.Utils import *
from MADBuf.SubjectGraph import *
from MADBuf.DataFlowGraph import *

class OptimizerBase:
    """Optimizer Base Class

    This is the base class for all optimizers
    """

    def __init__(self, *args, **kwargs) -> None:

        self.graph: BLIFGraph
        self.signal_to_channel: dict
        self.signals_in_component: dict
        
        self.top_module_name: str

        self.dfg: pgv.AGraph
        self.dfg_mapped: pgv.AGraph
        self.mapping: FloatingPointMapping

        self.signal_to_cuts: dict

        self.verbose: bool

        self.parse_top_module_name(*args, **kwargs)
        self.parse_dfg(*args, **kwargs)
        self.parse_graph(*args, **kwargs)
        self.parse_verbose(*args, **kwargs)


    def run_optimization(self, *args, **kwargs):
        raise NotImplementedError
    
    def get_solution(self, *args, **kwargs):
        raise NotImplementedError
    
    def parse_top_module_name(self, *args, **kwargs):
        # get the top module name, if not specified, raise an exception
        top_module_name: str = get_value_from_kwargs(kwargs, [
            'top_module_name',
            'top_module',
            'top',
            'name',
            'mut',
        ], None)

        if top_module_name is None:
            raise Exception('Top module name is not specified')
        
        self.top_module_name = top_module_name
        
    def parse_graph(self, *args, **kwargs):
        # get the subject graph, if not specified, raise an exception
        graph = get_value_from_kwargs(kwargs, [
            'graph',
            'subject_graph',
        ], None)

        if graph is None:
            raise Exception('Subject graph is not specified')
        
        network, signal_to_channel, signals_in_component = retrieve_anchors(graph)

        self.graph = network
        
        self.signal_to_channel = signal_to_channel
        
        self.signals_in_component = signals_in_component

        self.dfg_mapped = retrieve_data_flow_graph(signal_to_channel)

    def parse_dfg(self, *args, **kwargs):
        # get the data flow graph, if not specified, raise an exception
        dfg = get_value_from_kwargs(kwargs, [
            'dfg',
            'data_flow_graph',
        ], None)

        if dfg is None:
            raise Exception('Data flow graph is not specified')
        
        self.dfg = dfg

        has_floating: bool = has_floating(dfg)

        if not has_floating:
            return

        # get the mapping if any
        mapping = get_value_from_kwargs(kwargs, [
            'mapping',
            'mappings',
            'map',
            'maps',
        ], None)

        if mapping is None:
            raise Exception('Mapping is not specified')
        
        if isinstance(mapping, str):
            self.mapping = read_mapping(mapping)
        else:
            self.mapping = mapping
            
    def parse_signal_to_cuts(self, *args, **kwargs):
        # get the signal to cuts, if not specified, raise an exception
        signal_to_cuts = get_value_from_kwargs(kwargs, [
            'signal_to_cuts',
            'signal_to_cut',
        ], None)

        if signal_to_cuts is None:
            raise Exception('Signal to cuts is not specified')
        
        self.signal_to_cuts = signal_to_cuts

    def parse_verbose(self, *args, **kwargs):
        # get the verbose flag, if not specified, set it to False
        verbose: bool = get_value_from_kwargs(kwargs, [
            'verbose',
            'v',
        ], False)
        
        self.verbose = verbose
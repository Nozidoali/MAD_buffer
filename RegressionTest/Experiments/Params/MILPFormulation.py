#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-28 16:47:32
Last Modified by: Hanyu Wang
Last Modified time: 2023-04-02 14:37:46
'''

class MilpFormulationParams:

    def __init__(self) -> None:
        self.clock_period = 7
        self.cut_loopback_delay_propagation=False
        self.add_blockbox_constraints_flag=False
        self.add_blackbox_delay_propagation_flag=False
        self.add_cut_buffer_interaction_constraints_flag=False
        self.map_icmp=False

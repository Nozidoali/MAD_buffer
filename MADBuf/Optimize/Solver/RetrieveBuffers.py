#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-19 00:21:26
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-19 00:25:18
'''

import gurobipy as gp
from MADBuf.Utils import *
from MADBuf.Optimize.Variables import *

def retrieve_buffers(model: gp.Model, verbose: bool = False):

    num_buffered_channels: int = 0

    buffers: set = set()

    for variable in model.getVars():
        var_name: str = variable.varName
        # collect all the buffers
        if "_flop_ready" in var_name or "_flop_valid" in var_name:

            if variable.x == 0:
                continue

            num_buffered_channels += 1

            channel_type = (
                Constants._channel_ready_
                if "_flop_ready" in var_name
                else Constants._channel_valid_
            )

            component_from, component_to = variable_name_to_components(var_name)
            channel = Channel(component_from, component_to, channel_type)

            buffers.add(channel)

            # and, we also need the buffer

    if verbose:
        print("Number of buffered channels: ", num_buffered_channels)

    return buffers
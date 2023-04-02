#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-03-18 23:43:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-19 02:32:40
"""

from MADBuf.Optimize.Variables import *
from MADBuf.Optimize.ModelUtils.ChannelToVariable import *
from MADBuf.DataFlowGraph import *
from MADBuf.Network import *
import gurobipy as gp
import pygraphviz as pgv


def get_signal_to_variable(
    model: gp.Model,
    signal_to_channel: dict,
    dfg_mapped: pgv.AGraph,
    mapping: ComponentMapping = None,
    **kwargs,
) -> dict:

    signal_to_variable: dict = {}
    constria_cnts_to_add: set = set()

    verbose = get_value_from_kwargs(
        kwargs,
        [
            "verbose",
        ],
        False,
    )

    add_constraints = get_value_from_kwargs(
        kwargs,
        [
            "add_constraints",
            "add_cutloopback_constraints_flag",
        ],
        False,
    )

    # we first get the channel to variable mapping
    channel_to_var = get_equivalent_channel_to_variable(model, mapping)

    if mapping is not None:
        equivalent_to_functioning_mapping = (
            mapping.export_mapping_equivalent_to_functioning()
        )
    else:
        equivalent_to_functioning_mapping = {}

    # then we get the signal to channel mapping

    if not isinstance(signal_to_channel, dict):
        raise TypeError("signal_to_channel is not a dict")

    for signal in signal_to_channel:
        prev_channel: Channel = signal_to_channel[signal]

        equivalent_channel: Channel = get_equivalent_channel(dfg_mapped, equivalent_to_functioning_mapping, prev_channel)


        if equivalent_channel is None:
            continue

        if equivalent_channel in channel_to_var:
            matched_var = channel_to_var[equivalent_channel]

            if verbose:
                var_name = matched_var.getAttr("VarName")
                # print_green(f"Matched: {signal} to {var_name}")
            signal_to_variable[signal] = matched_var

            if verbose:
                # print_green(f"{signal} is found in the dynamatic model")
                pass
        else:
            print_red(f"Warning: {signal} is not found in the dynamatic model")
            pass

    return signal_to_variable

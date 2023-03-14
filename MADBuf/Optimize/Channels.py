#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-07 05:52:02
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-14 17:54:22
'''

import gurobipy as gp
from gurobipy import GRB
from MADBuf.Network.BLIFGraph import *
from MADBuf.Utils import *
from MADBuf.DataFlowGraph import *

def parse_dynamatic_channel_name(var_name: str, mappings: FloatingPointMapping = None):

    entries = var_name.split("_")

    component_from = f"{entries[0]}_{entries[1]}"
    component_to = f"{entries[2]}_{entries[3]}"

    if mappings is not None:
        maps = mappings.export_mapping_floating_to_unfloating()
        if component_from in maps:
            (component_from, buffer_inserted) = maps[component_from]
            component_type, component_index = component_from.split("_")

            if buffer_inserted:
                component_from = f"Buffer_{component_index}"

        if component_to in maps:
            component_to, buffer_inserted = maps[component_to]

            # insert buffer does not influence the component_to
            pass

    return component_from, component_to


def get_out_edges(signal_to_channel: dict):

    out_edges: dict = {}

    for signal in signal_to_channel:
        channel: Channel = signal_to_channel[signal]

        if channel.t != Constants._channel_valid_:
            continue

        out_edges[channel.u] = channel.v

    return out_edges


def get_channel_to_var(model: gp.Model, mappings: FloatingPointMapping = None):

    channel_to_var: dict = {}
    for var in model.getVars():
        var_name = var.getAttr("VarName")

        if "_flop_ready" in var_name or "_flop_valid" in var_name:
            component_from, component_to = parse_dynamatic_channel_name(
                var_name, mappings
            )

            channel_type = (
                Constants._channel_ready_
                if "_flop_ready" in var_name
                else Constants._channel_valid_
            )

            c: Channel = Channel(
                u=component_from, v=component_to, t=channel_type, idx=0
            )
            channel_to_var[c] = var

    return channel_to_var


def get_signal_to_channel_variable_mapping(
    model: gp.Model,
    network: BLIFGraph,
    signal_to_channel: dict,
    add_constraints: bool = True,
    mappings: FloatingPointMapping = None,
    verbose: bool = False,
):
    """
    we need to find the variable names defined in dynamatic linear programs

    """

    # we first get the channel to variable mapping
    channel_to_var = get_channel_to_var(model, mappings)

    # we precompute the out edges for each component
    out_edges = get_out_edges(signal_to_channel)

    # we prepare the set of all the floating point components
    unfloating_components = set()

    # we skip if mappings does not exists at all
    if mappings != None:
        maps = mappings.export_mapping_floating_to_unfloating()
        for floating in maps:
            unfloating, insert_buffer = maps[floating]

            if insert_buffer:
                unfloating_components.add(unfloating)

    signal_to_channel_var: dict = {}

    # now we do the matching
    for signal in network.signals:

        if signal in signal_to_channel:
            c: Channel = signal_to_channel[signal]

            # a buffer need to be inserted no matter what
            has_buffer: bool = False

            # we don't have a seperate variable for the data channel
            if c.t == Constants._channel_data_:
                c.t = Constants._channel_valid_

            # we skip all the channels inside floating point components
            if c.u in unfloating_components:
                continue

            # we skip all the channels that are connected already to the buffers
            #
            #                    Component A
            #                      |   |    <--- this channel is skipped
            #                     V|   |R
            #                ->    |   |
            #                      Buffer
            #                      |   |
            #                     V|   |R
            #                      |   |
            #                    Component B
            if "Buffer" in c.v:

                assert c.v in out_edges

                # bypass the buffer
                c.v = out_edges[c.v]

                # TODO: now we assume that the channel is always a valid signal
                # and we don't consider the case where more than one buffer is on the channel
                if c.t == Constants._channel_valid_:

                    if c not in channel_to_var:
                        print_red(f"Channel {c} is not found in the dynamatic model")
                        raise Exception("Channel not found in the dynamatic model")

                    assert c in channel_to_var
                    matched_var = channel_to_var[c]
                    has_buffer = True

                # we need to add a constraint to make sure the buffer is used
                if add_constraints:
                    model.addConstr(matched_var >= 1)

                if verbose:
                    var_name = matched_var.getAttr("VarName")
                    print_green(f"Adding constraint: {var_name} >= 1")

                # we don't need to consider the buffer channel
                continue

            if c in channel_to_var:
                matched_var = channel_to_var[c]

                if verbose:
                    var_name = matched_var.getAttr("VarName")
                    # print_green(f"Matched: {signal} to {var_name}")
                signal_to_channel_var[signal] = matched_var
                
                if verbose:
                    # print_green(f"{signal} is found in the dynamatic model")
                    pass
            else:
                # TODO: we should not add this variable
                # new_var = model.addVar(vtype=GRB.BINARY, name=f"new_{c.u}_{c.v}_{c.t}")
                # signal_to_channel_var[signal] = new_var

                if verbose:
                    # print_red(f"Warning: {signal} is not found in the dynamatic model")
                    pass

    return signal_to_channel_var

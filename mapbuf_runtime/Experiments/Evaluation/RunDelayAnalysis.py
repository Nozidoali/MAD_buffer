#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-04-11 19:32:15
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-13 09:37:09
'''

from ..Path import *
import numpy as np

def run_delay_analysis(setup_timing_report_path: str, n_paths_to_analyze: int, verbose: bool = False):
    

    print(f"running delay analysis on {setup_timing_report_path} ...", end=" ", flush=True)
    with open(setup_timing_report_path, "r") as f:
        lines = f.readlines()

        path_start: int = 0
        curr_state: str = "idle"
        curr_delay_type: str = "wire-delay"


        data_arrival_times: list = []
        wire_delays: list = []
        logic_delays: list = []
        logic_wire_delays: list = []
        dual_port_ram_delays: list = []
        multiplier_delays: list = []
        lut_level_delays: list = []

        adder_delays: list = []

        curr_n_paths = 0
        curr_adder_delay = 0
        curr_adder_chain_length = 0
        curr_adder_name = None

        wire_delay_type = 'logic'
        
        i: int = 0
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            if line.startswith("Point") and len(line.split()) == 3 and line.split()[1] == "Incr" and line.split()[2] == "Path":
                assert curr_state == "idle"
                path_start = i
                i += 1 # skip the next line
                curr_state = "path"
                continue

            if line.startswith("data arrival time"):
                # assert curr_state == "path"
                if curr_state != "path":
                    continue

                curr_n_paths += 1
                if curr_n_paths > n_paths_to_analyze:
                    break

                data_arrival_time = float(line.split()[-1])

                
                curr_state = "idle"
                data_arrival_times.append(data_arrival_time)
                continue

            if curr_state == "path":
                data = line.split()
                try:
                    incr = float(data[-2])
                    path = float(data[-1])
                    name = ' '.join(data[0:-2])
                except:
                    raise Exception(f"error parsing line {i}: {line}")
                
                if incr == 0:
                    continue

                if verbose:
                    print(f"{name}: {curr_delay_type} (path: {path}, incr: {incr})")


                if "(adder)" in name:
                    wire_delay_type = 'adder'
                    
                    # we keep track of the delay of the last adder in the path
                    adder_name = name.split("^")[0].strip()
                    
                    # print(f"{adder_name} ({name}), curr_adder_delay = {curr_adder_delay}, incr = {incr}")

                    # if the current adder is different from the last one, we add the delay of the last adder to the adder_delays list
                    # and reset the curr_adder_delay to 0
                    if curr_adder_name == None or curr_adder_name != adder_name:
                        if curr_adder_delay != 0:
                            # print("length of adder chain:", curr_adder_chain_length, "adder delay:", curr_adder_delay)

                            # we only consider adder chains with length > 16
                            # because adder chains with length <= 16 are not critical
                            # and probably not using DSPs
                            if curr_adder_chain_length > 16:
                                adder_delays.append(curr_adder_delay + incr)
                        curr_adder_name = adder_name
                        curr_adder_delay = incr
                        curr_adder_chain_length = 0
                    
                    # if the current adder is the same as the last one, we add the incr to the curr_adder_delay
                    else:
                        curr_adder_delay += incr
                        curr_adder_chain_length += 1

                else:
                    # if the current adder is the same as the last one, we add the incr to the curr_adder_delay
                    if curr_adder_name != None and curr_adder_delay != 0:
                        # print("length of adder chain:", curr_adder_chain_length, "adder delay:", curr_adder_delay)

                        # we only consider adder chains with length > 16
                        # because adder chains with length <= 16 are not critical
                        # and probably not using DSPs
                        if curr_adder_chain_length > 16:
                            adder_delays.append(curr_adder_delay + incr)
                        curr_adder_delay = incr
                        curr_adder_chain_length = 0
                        curr_adder_name = None


                if curr_delay_type == "wire-delay":
                    wire_delays.append(incr)

                elif curr_delay_type == "logic-delay":

                    if "dual_port_ram" in name:
                        dual_port_ram_delays.append(incr)
                        wire_delay_type = 'ram'

                    elif "(multiply)" in name:
                        multiplier_delays.append(incr)
                        wire_delay_type = 'multiplier'

                    elif ".out[" in name and "(.names)" in name:
                        if incr not in [0.235, 0.261]:
                            print(f"{name}: {curr_delay_type} (path: {path}, incr: {incr})")
                            raise Exception(f"error parsing line {i}: {line}")
                        
                        logic_delays.append(incr)

                        # this is not a logic delay, but a carry chain delay
                        effective_wire_delay = wire_delays[-1] if wire_delay_type == 'lut' else 0

                        if effective_wire_delay == 0:
                            pass
                
                        else:
                        
                            # this is a hack to fix the issue that the wire delay of the last lut is not included in the logic delay
                            lut_level_delays.append(incr + effective_wire_delay)

                            logic_wire_delays.append(effective_wire_delay)
                        
                        wire_delay_type = 'lut'
                
                # toggle delay type
                if curr_delay_type == "wire-delay":
                    curr_delay_type = "logic-delay"
                elif curr_delay_type == "logic-delay":
                    curr_delay_type = "wire-delay"
       

    print_green("Done")

    if verbose:
        print(f"found {len(data_arrival_times)} data arrival times")
        print(f"found {len(wire_delays)} wire delays")
        print(f"average wire delay: {sum(wire_delays)/len(wire_delays)}")
        print(f"stderr wire delay: {np.std(wire_delays)}")
        print(f"found {len(logic_delays)} logic delays")
        print(f"average logic delay: {sum(logic_delays)/len(logic_delays)}")
        print(f"stderr logic delay: {np.std(logic_delays)}")

    return logic_delays, logic_wire_delays, lut_level_delays, adder_delays

def run_delay_analysis_from_kwargs(**kwargs):

    setup_timing_report_path = get_setup_timing_report_path_from_kwargs(**kwargs)

    n_paths_to_analyze = get_value_from_kwargs(kwargs, "n_paths_to_analyze", 1)
    n_paths_to_analyze = 100

    return run_delay_analysis(setup_timing_report_path, n_paths_to_analyze)
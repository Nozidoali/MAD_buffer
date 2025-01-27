#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-28 18:03:15
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-13 09:36:20
'''

from ..Path import *
from mapbuf import *

def cut_enumeration_from_kwargs(network: BLIFGraph, signal_to_channel: dict, **kwargs):

    ext_cut_file_flag = get_value_from_kwargs(kwargs, [
        "ext_cut_file",
    ], False)


    if ext_cut_file_flag is True:
        """
        Load external cut files
        """
        ext_cut_file = get_cuts_path_from_kwargs(**kwargs)
        print(f"Loading external cut files {ext_cut_file}...", end=' ', flush=True)
        signal_to_cuts = read_cuts(ext_cut_file)
        print_green("Done", flush=True)
        
    else:
        signal_to_cuts = cut_enumeration(
            network, 
            signal_to_channel=signal_to_channel,
            **kwargs
        )

        cut_path = get_cuts_path_from_kwargs(**kwargs)
        print(f"Writing cuts to {cut_path} ...", end='', flush=True)
        write_cuts(signal_to_cuts, cut_path)
        print_green("Done", flush=True)

    return signal_to_cuts
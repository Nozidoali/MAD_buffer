#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-21 15:28:35
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-26 00:38:43
'''

from MADBuf.Network import *
from MADBuf.Synthesis.TimingLabel import TimingLabel
from MADBuf.Utils import *
from MADBuf.Synthesis.CutEnumeration.ExpandCutBase import *
from MADBuf.Synthesis.CutEnumeration.ZeroOrderCutExpansion import *
from MADBuf.Synthesis.CutEnumeration.FirstOrderCutExpansion import *
from MADBuf.Synthesis.CutEnumeration.AllBufferedCutExpansion import *

class cut_preparation_params:

    use_zero_order_cut: bool = True
    use_first_order_cut: bool = False
    use_infinite_order_cut: bool = True
    use_all_buffered_cut: bool = False

def precompute_timing_labels(
    g: BLIFGraph,
    signal_to_channel: dict = {},
    cut_size_limit: int = 6,
    max_expansion_level: int = 0,
    verbose: bool = False,
) -> tuple:
    """Get timing labels

    Args:
        g (BLIFGraph): the subject graph
        signal_to_channel (dict, optional): the mapping from signals to the channels. Defaults to {}.
        cut_size_limit (int, optional): the K value in K-LUT mapping. Defaults to 6.
        max_expansion_level (int, optional): the expansion level in which we torelant the cut size violation. Defaults to 0 (zero tolerance).

    Returns:
        tuple (dict, dict): (labels, cuts)
    """
    
    if verbose:
        print(f"Precompute timing labels, cut size limit = {cut_size_limit}")

    labels: dict = {}
    all_buffered_labels: dict = {}
    signal_to_cuts: dict = {}

    channel_to_signals: dict = {}
    for signal in signal_to_channel:
        channel = signal_to_channel[signal]
        if channel not in channel_to_signals:
            channel_to_signals[channel] = []
        channel_to_signals[channel].append(signal)

    for signal in g.topological_traversal():
        signal_to_cuts[signal] = []
        cuts = []

        if g.is_ci(signal):
            labels[signal] = TimingLabel(0)
            all_buffered_labels[signal] = TimingLabel(0)
            signal_to_cuts[signal] = [Cut(signal, [signal])]
            continue

        if cut_preparation_params.use_zero_order_cut:
            optimal_timing_label, zero_order_cut = zero_order_cut_expansion(
                g,
                signal=signal,
                labels=labels,
                signal_to_channel=signal_to_channel,
                cut_size_limit=cut_size_limit,
                max_expansion_level=max_expansion_level,
            )
            labels[signal] = optimal_timing_label

            cuts.append(zero_order_cut)

        if cut_preparation_params.use_first_order_cut:
            assert cut_preparation_params.use_zero_order_cut
            
            first_order_timing_label, first_order_cut = first_order_cut_expansion(
                g,
                cut=zero_order_cut,
                labels=labels,
                signal_to_channel=signal_to_channel,
                channel_to_signals=channel_to_signals,
                cut_size_limit=cut_size_limit,
                max_expansion_level=max_expansion_level,
                verbose=verbose,
            )

            if first_order_timing_label is not None:
                if first_order_timing_label < optimal_timing_label:

                    cuts.append(first_order_cut)

        if cut_preparation_params.use_infinite_order_cut:
            # infinite order cuts
            cuts.append(Cut(signal, g.node_fanins[signal]))

        if cut_preparation_params.use_all_buffered_cut:
            if signal in signal_to_channel:
                all_buffered_labels[signal] = TimingLabel(0)

                # we don't add cuts to these channel signals
                pass

            else:
                # then we add the cuts assuming all the channels are buffered
                all_buffered_timing_label, all_buffered_cut = all_buffered_cut_expansion(
                    g,
                    signal=signal,
                    labels=all_buffered_labels,
                    signal_to_channel=signal_to_channel,
                    channel_to_signals=channel_to_signals,
                    cut_size_limit=cut_size_limit,
                    max_expansion_level=max_expansion_level,
                    verbose=verbose,
                )
                if all_buffered_timing_label is not None:
                    all_buffered_labels[signal] = all_buffered_timing_label
                    if all_buffered_timing_label < optimal_timing_label:
                        cuts.append(all_buffered_cut)
                
        signal_to_cuts[signal] = cuts
        
        # unique cuts
        signal_to_cuts[signal] = list(set(signal_to_cuts[signal]))

    return labels, signal_to_cuts
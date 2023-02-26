from Optimize.MilpConstructor import MilpConstructor
from Optimize.OptimizeThroughput import *
from Parsers.DynamaticDOT import *
from Parsers.DummyBlif import *

from TestCases import *


def test_cutless():
    g: BLIFGraph = small_blif()
    network, _, _ = g.retrieve_anchors()

    cutless_enumeration(network)


def test_milp_constructor():
    g: BLIFGraph = small_blif()

    network, signal_to_channel, node_in_component = g.retrieve_anchors()

    channels: list = []
    for node in signal_to_channel:
        channel = signal_to_channel[node]
        channels.append(str(channel))

    constructor = MilpConstructor()
    cuts = cutless_enumeration(network)

    constructor.add_timing_label_variables(network)
    constructor.add_input_delay_constraints(network)
    constructor.add_clock_period_constraints(network)
    constructor.add_madbuf_constraints(cuts)
    constructor.add_channel_buffer_varibles(channels)
    constructor.export_lp("test_lp.lp")


def test_throughput_optimization():
    optimizer = ThroughputOptimizer()
    g: BLIFGraph = BLIFGraph("./Examples/gsum/gsum.blif")

    optimizer.read_dynamatic_lps("./Examples/gsum/gsum.lp")
    optimizer.add_timing_constraints(g)
    # optimizer.run()


if __name__ == "__main__":
    # test_cutless()

    test = TestThroughputOptimization()

    test.run()

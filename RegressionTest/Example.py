from MADBuf import *

import subprocess

g: BLIFGraph = read_blif("dummy/reports/dummy.blif")
network, signal_to_channel, signals_in_component = retrieve_anchors(g)

dfg = read_dfg("dummy/reports/dummy.dot")

cuts = cut_enumeration(
    network, cut_size=6, num_cuts=100, cutless=True, signal_to_channel=signal_to_channel
)
signal_to_cuts = cleanup_dangling_cuts(cuts)

optimizer = Optimizer(
    top="dummy",
    graph=g,
    dfg=dfg,
    signal_to_cuts=signal_to_cuts,
    clock_period=4,
    target="latency",
)

optimizer.run_optimization(
    time_limit=100,
    lp_filename="dummy_buf.lp",
    ilp_filename="dummy_buf.ilp",
    solution_filename="dummy_buf.sol",
)

dfg: pgv.AGraph = optimizer.get_solution()
write_dfg(dfg, "dummy_buf.dot")
run("dot -Tpng dummy_buf.dot -o dummy_buf.png", shell=True)

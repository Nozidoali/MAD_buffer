from MADBuf import *
from TestCases.TestCases import TestCases

class TestMADBuf(TestCases):
    def __init__(self) -> None:
        pass

    def run(self) -> None:
        
        blif: BLIFGraph = BLIFGraph("./Examples/gsum/gsum.blif")
        
        dot: pgv.AGraph = read_dynamatic_dot("./Examples/gsum/gsum.dot")
        
        network, signal_to_channel, node_in_component = blif.retrieve_anchors()
        
        # these two methods work the same
        optimizer: MADBuf = MADBuf(network, signal_to_channel, node_in_component)
        # optimizer: MADBuf = MADBuf(blif)
        
        buffers, maximum_timing = optimizer.run(clock_period=4, verbose=False)

        insert_buffers_in_dfg(dot, buffers=buffers, verbose=False)
        buffer_blackboxes(dot)
        
        mapping = load_mapping_from_file("./mapping/gsum.map")
        
        fix_floating_point_components(dot, mapping)
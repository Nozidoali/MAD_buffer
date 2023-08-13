#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-11 21:08:49
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-13 09:20:53
'''

from mapbuf import *
from TestCases.TestCases import *
from TestCases.Generators import *

class TestVerilogReader(TestCases):

    def test(self) -> None:
        for file in fpl_verilog_files():
            verilog = read_verilog(file)
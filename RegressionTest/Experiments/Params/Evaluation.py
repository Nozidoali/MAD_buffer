#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-03-28 18:28:38
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-28 18:30:05
'''

class EvaluationParams:

    def __init__(self) -> None:
        self.run_synthesis = True
        self.check_timing_flag = True
        self.check_cycle_flag = True
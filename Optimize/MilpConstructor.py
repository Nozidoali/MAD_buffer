import gurobipy as gp
from gurobipy import GRB
from Parsers.BLIFGraph import *
from Optimize.MilpFormulation import *


class MilpConstructor:
    def __init__(self, model=None) -> None:
        self.signal_to_variable: dict = {}
        self.channel_to_variable: dict = {}

        if model == None:
            self.model: gp.Model = gp.Model("new_model")

        else:
            self.model = model

    def add_timing_label_variables(self, g: BLIFGraph):

        for signal in g.signals:
            var_signal = self.model.addVar(
                vtype=GRB.INTEGER, name=f"TimingLabel_{signal}"
            )  # delay variables

            # remember this variable in the dictionary
            self.signal_to_variable[signal] = var_signal

            # otherwise the variable names will not be found
            #   reference:
            #       https://stackoverflow.com/questions/66182055/pythongurobiattributeerror-index-out-of-range-for-attribute-varname
            # 
            self.model.update()

    def add_clock_period_constraints(self, g: BLIFGraph, target_period: int = milp_params.infinity):
        """
        signal constraints:
            for each signal in the subject, the latency should be smaller than the target period
        """
        self.var_cp = self.model.addVar(vtype=GRB.INTEGER, name=f"CP")

        for signal in g.signals:
            var_signal = self.signal_to_variable[signal]

            self.model.addConstr(var_signal >= 0)
            self.model.addConstr(var_signal <= self.var_cp)

        # set the target clock period here
        self.model.addConstr(self.var_cp <= target_period)

        self.model.update()

    def add_input_delay_constraints(self, g: BLIFGraph, input_delays: dict = None):

        if input_delays != None:
            """
            we will allow users to specify the input delays (arrival times at the module inputs)
            """
            return NotImplementedError

        else:
            """
            By default we assume all input delays = 0
            """
            for input_signal in g.inputs.union(g.ros):

                # the signals should be defined before calling this function
                assert input_signal in self.signal_to_variable

                var_input_signal = self.signal_to_variable[input_signal]
                self.model.addConstr(
                    var_input_signal == 0, f"InputDelay_{input_signal}"
                )
        
        self.model.update()

    def add_channel_buffer_varibles(self, channels: list):
        for channel_name in channels:
            var_channel = self.model.addVar(vtype=GRB.INTEGER, name=f"{channel_name}")

            self.channel_to_variable[channel_name] = var_channel
        
        self.model.update()


    def add_madbuf_constraints(self, signal_to_cuts: dict, signal_to_channel_var: dict = None):

        for signal in signal_to_cuts:

            # delay propagation
            var_signal = self.signal_to_variable[signal]

            # find the buffer variable
            # buffer_var is None, when:
            #  1. the signal is not in signal_to_channel_var
            #  2. the signal is in signal_to_channel_var, but the value is None
            #  3. the signal_to_channel_var is None
            #
            try: 
                buffer_var = signal_to_channel_var[signal]
            except:
                buffer_var = None

            # get the set of cuts that are precomputed for this signal
            cut_set: list = signal_to_cuts[signal]
            n_cuts = len(cut_set)

            cut_selection_vars: list = []
            # for each cut in the set set
            for cut_index in range(n_cuts):

                cut = cut_set[cut_index]

                # cut selection variables
                var_cut_selection = self.model.addVar(
                    vtype=GRB.BINARY, name=f"Y({signal}->{cut_index})"
                )
                cut_selection_vars.append(var_cut_selection)

                # @see MilpFormulation.py
                add_timing_constraints(self.model, signal, cut, var_cut_selection)

            # at least one cut need to be chosen
            # reference: https://www.gurobi.com/documentation/10.0/refman/py_model_addconstrs.html
            self.model.addConstr(
                sum(cut_selection_vars) == 1, f"cut_selection_at_{signal}"
            )

    def export_lp(self, lp_name: str):
        assert lp_name.endswith(".lp")

        self.model.write(lp_name)

    def export_solution(self, sol_name: str):
        assert sol_name.endswith(".sol")

        self.model.write(sol_name)

    def print_throughput(self):
        for var in self.model.getVars():

            var_name: str = var.getAttr("VarName")
            var_value = var.getAttr("X")

            if var_name.startswith("x") and var_name[1:].isdigit():
                print(f"throughput ({var_name}) = {var_value}")

    def print_buffers(self):
        for var in self.model.getVars():

            var_name: str = var.getAttr("VarName")
            var_value = var.getAttr("X")

            if "hasBuffer" in var_name and var_value > 0:
                print(f"{var_name} = {var_value}")

    def optimize(self):
        self.export_lp("test_lp.lp")
        self.model.optimize()
        self.print_throughput()
        self.print_buffers()
        self.export_solution("test_lp.sol")

    def optimize_clock_period(self):
        self.model.setObjective(self.var_cp, GRB.MINIMIZE)
        self.export_lp("test_lp.lp")
        self.model.optimize()
        self.export_solution("test_lp.sol")

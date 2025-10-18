import numpy
import numpy as np
from utils import dprinter

class Cooler:
    def __init__(self):
        """

        Simulates a cooler which sets a cooling rate to be applied to an external system.

        cooler_param functions as a process variable in a PID control feedback loop.

        """
        self.cooler_param = 0
        self.max_cool = 35/60
        self.min_cool = 3/60
        self.param_range = [0, 1]
        self.debug = False
        self.dprinter = dprinter(debug=self.debug)
        self.print = self.dprinter.print

    def toggle_debug(self):
        """
        Toggles the debug flag for printing.
        """

        self.debug = not self.debug
        self.dprinter.debug = self.debug

    def set_cooler_param(self, val):
        """
        Sets the cooler param to the provided value

        :param val: float
        """

        self.cooler_param = val
        self.print(msg=f"Setting cooler param: {val}")

    def cooling_function(self, method="step") -> float:
        """

        Simple 5 stage curve for cooling rate based on function.

        This could be a function, but I thought the idea of a slow transition between minimum heat transfer (>0) and
        maximum heat transfer would simulate a pump that is subject to system momentum.

        :param method: method selector for the cooling function, either step or other (linear f(x))
        :return:
        """

        if method == "step":
            cooling_steps = np.linspace(self.min_cool, self.max_cool, 5)
            if self.cooler_param <= self.param_range[0]:
                self.print(f"Running cooler at State 1 minimum rate: {-1*cooling_steps[0]}")
                self.cooler_param = self.param_range[0]
                return -1 * cooling_steps[0]
            elif self.cooler_param < self.param_range[1]/3:
                cool_rate = -1 * (cooling_steps[1])
                self.print(f"Running cooler at Stage 2 rate: {cool_rate}")
                return cool_rate
            elif self.cooler_param < 2*self.param_range[1]/3:
                cool_rate = -1 * cooling_steps[2]
                self.print(f"Running cooler at Stage 3 rate: {cool_rate}")
                return cool_rate
            elif self.cooler_param < self.param_range[1]:
                cool_rate = -1 * cooling_steps[3]
                self.print(f"Running cooler at Stage 4 rate: {cool_rate}")
                return cool_rate
            else:
                self.print(f"Running cooler at Stage 5 maximum rate{-1*self.max_cool}")
                self.cooler_param = self.param_range[1]
                return -1 * self.max_cool
        else:
            return -5*self.cooler_param

    def get_cooling_rate(self) -> float:
        """
        :return: Cooling rate (C/s) for current parameters
        """
        return self.cooling_function()

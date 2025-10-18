from utils import dprinter
import time
import numpy as np
from datetime import datetime


class CanOfSoda:
    def __init__(self):
        """

        Simulates a particularly special can of soda that has it's own heating element.

        Monitors the temperature of the can, and handles the temperature increase due to internal and external sources.

        """

        self.temperature = 23  # C
        self.internal_heater = 2 / 60  # C/s
        self.external_heat_exchange = 5 / 60  # C/s
        self.critical_temperature = 49  # C
        self.critical_trigger = False
        self.temperature_history = []
        self.internal_time = 0
        self.dt = 1
        self.debug = False
        self.dprinter = dprinter(debug=self.debug)
        self.print = self.dprinter.print
        self.include_disturbance = True

        self.shelf = []
        self.report_interval = 5

    # region helpers
    def toggle_debug(self):
        """
        Toggles the debug statement.
        """

        self.debug = not self.debug
        self.dprinter.debug = self.debug

    @staticmethod
    def celcius_to_kelvin(val) -> float:
        """

        Converts celcius to kelvin

        :param val: temperature in Celcius
        """

        return val + 253.15

    @staticmethod
    def kelvin_to_celcius(val) -> float:
        """
        Converts kelvin to celcius
        :param val: Temperature in Kelvin.
        :return:
        """
        return val - 253.15

    # endregion

    # region process
    def update_temperature(self):
        """

        Updates the system temperature using all system parameters and logic.

        """
        self.print(
            f"Updating Temperatures by summing "
            f"T: {self.temperature} "
            f"Hi: {self.internal_heater} "
            f"Ho {self.external_heat_exchange}")

        operational_heater = self.internal_heater

        if self.include_disturbance:
            self.internal_time += self.dt
            if 25 * 60 <= self.internal_time % (60 * 60) <= 35 * 60:
                operational_heater = self.internal_heater + 4 / 60

        self.temperature = self.temperature + operational_heater * self.dt + self.external_heat_exchange * self.dt
        self.check_temp_conditions()
        self.temperature_history.append(self.temperature)

    def check_temp_conditions(self):
        """

        Checks the current temperature and compares it against the critical temperature, raises a flag if temperature
        is too high, lowers the flag once the temperature is low enough.

        :return:
        """
        if self.temperature > self.critical_temperature * 0.75:
            self.critical_trigger = True
            print(f"{datetime.now()} :: "
                  f"WARNING: SODA TEMPERATURE {self.temperature:0.2f}C, "
                  f"MAX ALLOWED TEMPERATURE OF {self.critical_temperature}C")
        else:
            if self.critical_trigger:
                print(f"{datetime.now()} :: "
                      f"Info: Critical temperature warning ended, temperature in safe zone."
                      f" T<{self.critical_temperature * 0.75}C")
                self.critical_trigger = False

    # endregion

    # region setters/getters

    def set_external_heat(self, val):
        """

        Sets the external heat source value

        :param val: float, C/s
        """

        self.external_heat_exchange = val

    def set_temperature(self, val):
        """

        Sets the temperature variable of the tank

        :param val: float, C
        """

        self.temperature = val

    def get_temperature(self, unit="C"):
        """

        Returns the current temperature in either C or K

        :param unit: string, C or K
        """
        if unit == "C":
            return self.temperature
        else:
            return self.celcius_to_kelvin(self.temperature)

    # endregion

    # region concurrent running

    def GetLiveReading(self) -> dict:
        """

        Checks if there a value has been produced and returns it, then clears the holder. If no value is present a dict
        with all values set to np.NaN is returned instead.

        :return: dict
        """

        if len(self.shelf) > 0:
            ret_val = self.shelf[0]
            self.shelf = []
            return ret_val
        else:
            # This is dirty, runs the risk of updating the LiveReading later with more values and needing to update it
            # here would want to create a base_dict that gets cleared and returned that can be quickly set to all np.NaN
            # for readings.
            ret_val = {
                "temperature": np.NaN,
                "time": np.NaN,
                "critical temp": np.NaN
            }

            return ret_val

    def SetLiveReading(self, value, time_obj):
        """

        Sets gives the values to the handler to make available to external software.

        :param value: Temperature value to place in the LiveReading results dictionary.
        :param time_obj: Time object used by the Tank to be placed into the LiveReading results dictionary
        """

        self.print(f"updating with {value}")

        ret_val = {
            "temperature": value,
            "time": time_obj,
            "critical temp": self.critical_temperature
        }

        self.shelf.append(ret_val)

    def run(self):
        """

        Begins the tank operation loop.

        :return:
        """

        while True:
            current_time = datetime.now()

            # always update the temperature
            self.update_temperature()

            if current_time.second % self.report_interval == 0:
                self.SetLiveReading(self.temperature, current_time)

            # wait dt second
            time.sleep(self.dt)

    # endregion

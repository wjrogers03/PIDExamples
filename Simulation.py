import dataclasses
import math
import numpy as np

from PID import PIDController
from Transmitter import Transmitter


@dataclasses.dataclass
class SimulationConfig:
    run_time: float
    delta_t: float

    @property
    def number_of_steps(self) -> int:
        return math.ceil(self.run_time/self.delta_t)

class Simulation:
    def __init__(self, config: SimulationConfig, process: Transmitter, controller: PIDController):
        self._config = config
        self._process = process
        self._controller = controller

        self._clock = 0.0

        self._time_data = np.ndarray(config.number_of_steps)
        self._process_data = np.ndarray(config.number_of_steps)

    @property
    def time_data(self) -> np.ndarray:
        return self._time_data
    
    @property
    def process_data(self) -> np.ndarray:
        return self._process_data
    
    def run(self) -> None:
        for i in range(self._config.number_of_steps):
            output = self._controller.output(self._process.value, self._config.delta_t)
            self._process.update(output, self._config.delta_t)

            self._time_data[i] = self._clock
            self._process_data[i] = self._process.value

            self._clock += self._config.delta_t

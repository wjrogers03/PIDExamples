import dataclasses

@dataclasses.dataclass
class PIDConfig:
    k_p: float = 0.0
    k_i: float = 0.
    k_d: float = 0.0
    setpoint: float = 0.0
    lower_bound: float = 0.0
    upper_bound: float = 0.0

class PIDController:
    def __init__(self, config: PIDConfig):
        self._config = config
        self.error = 0.0
        self.integral_error = 0.0
        self.derivate_error = 0.0

    def output(self, process_var: float,  dt: float) -> float:
        previous_error = self.error
        self.error = self._config.setpoint - process_var
        self.integral_error += self.error *dt
        self.derivate_error = (self.error - previous_error)/dt

        output = self._config.k_p*self.error + self._config.k_i*self.integral_error + self._config.k_d*self.derivate_error

        return output

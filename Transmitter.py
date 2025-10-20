import dataclasses

@dataclasses.dataclass
class Transmitter:
    value: float
    lag_time: float

    def update(self, new_value, dt):
        self.value += dt/self.lag_time*new_value
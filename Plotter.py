import matplotlib.pyplot as plt
import numpy as np

class Plotter:
    def __init__(self, setpoint: float = 0.0):
        self._fig, self._ax = plt.subplots(figsize=(3 * 3, 2 * 3))
        self._ax.axhline(y=setpoint, color='r', linestyle='--', label=f'Setpoint: {setpoint}')
        self._ax.set_xlabel("Time(s)")
        self._ax.set_ylabel("Process")
        self._ax.set_title("PID Controller Simulation")
        self._fig.legend()

    def add_plot(self, x_data: np.ndarray, y_data: np.ndarray, label: str) -> None:
        self._ax.plot(x_data, y_data, label=label)
        self._fig.legend()

    def show(self) -> None:
        self._fig.legend()
        plt.show()

from PID import PIDConfig, PIDController
from Plotter import Plotter
from Simulation import Simulation, SimulationConfig
from Transmitter import Transmitter

def main() -> None:
    setpoint = 35.0
    simulation_config = SimulationConfig(run_time=400.0, delta_t=0.01)
    plotter = Plotter(setpoint=setpoint)

    pid_configs = {
        "high_integral": PIDConfig(k_p=0.25, k_i=0.1, k_d=0.1, setpoint=setpoint),
        "well_tuned": PIDConfig(k_p=0.3, k_i=0.005,  k_d=0.05, setpoint=setpoint),
    }

    for tune_name, tune in pid_configs.items():
        transmitter = Transmitter(value=0.0, lag_time=5.0)
        pid_controller = PIDController(tune)
        simulation = Simulation(simulation_config, transmitter, pid_controller)
        simulation.run()
        plotter.add_plot(simulation.time_data, simulation.process_data, tune_name)

    plotter.show()

if __name__ == "__main__":
    main()

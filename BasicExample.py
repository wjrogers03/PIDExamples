import PID
import matplotlib.pyplot as plt
import time



def DirectProcessVal():
    """
    A simple PID feedback control system where the process variable and setpoint exist in the same space.
    """
    def MonitorSimulator():
        """
        Rules from assignment:
            Must:
                Take a set point
                process var
                tuning constants (Kp,Ki,Kd)
                return output.
                    These are handled by standard definitions of the PID controller
                Take into consideration integral windup
                    Added logic to controller to handle this, if conditional_integration = True the controller will
                    reset the integral value if it becomes larger than 25% of the setpoint on an absolute scale
                Limited between two values
                    Added a bounds parameter to the PID and is enabled via the bound_control bool

                Assume a step change in the controller setpoint from zero to 1 (see initial step in while loop)
                5 second lag time between process variable updates


                Tune constants to achieve a smooth response curve.
                    I have included an option to update the process var on every timestep to have a smooth response
                    curve.

                Plot the setpoint and controller output as a function of time.

        """

        process_temp = 0  # C,      initial temperature
        setpoint_temp = 35  # C,    target temperature
        lag_time = 5  # Seconds
        # controller = PID.Controller(Kp=0.25, Ki=0.1, Kd=0.1, setpoint=setpoint_temp) # for 48, 35
        controller = PID.Controller(Kp=0.3, Ki=0.005, Kd=0.05, setpoint=setpoint_temp)  # for 0, 35
        controller.conditional_integration = True
        controller.bound_control = True
        controller.bounds = [-10, 10]
        controller.step_size = dt
        # controller.toggle_debug()

        t = 0

        temp_history = []
        time_history = []

        update_process_every_timestep = True

        initial_step = True

        while True:
            # update system
            control_output = controller.calc(process_var=process_temp)

            if initial_step:
                process_temp += 1
                initial_step = False
            if not update_process_every_timestep:
                if t % lag_time == 0:
                    # update parameters
                    process_temp += control_output * dt
            else:
                process_temp += control_output * dt

            temp_history.append(process_temp)
            time_history.append(t)
            print(f"Simulation Time: {t}s")
            # advance the time.
            t += dt

            if t == 100:
                break

            # sleep for dt
            time.sleep(0.01)  # sleeping for 0.01 to speed up time, dt is still = 1


        plt.style.use("bmh")

        fig, ax = plt.subplots(figsize=(3 * 3, 2 * 3))
        ax.plot(time_history, temp_history, label='System Temperature', color="b")
        ax.axhline(y=setpoint_temp, color='r', linestyle='--', label=f'Target Temperature: {setpoint_temp}$\degree$C')
        ax.set_xlabel("Time(s)")
        ax.set_ylabel("Temperature ($\degree$C)")
        ax.set_title("PID Controller Simulation")
        plt.ylim(-20,120)

        plt.legend()
        plt.show()


    dt = 1
    MonitorSimulator()


DirectProcessVal()

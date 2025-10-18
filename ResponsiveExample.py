import TankCooler
import TankMonitor
import PID
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import threading
import time


def GetTargetTemperature(t=0, method="flat", tank_time=0):
    """

    Returns the target temperature for the system.

    :param t: current time
    :param method: If 24hour will return a target temperature based on a 24 hour cycle and param t.
    Else, returns a flat value.
    :param tank_time: The time associated with the simultaneously running TankMonitor object. Requires t=0.

    """

    # only a bit of DNR going on here, I'm coming up on my self-imposed timelimit...

    if tank_time == 0:
        if method == "24hour":
            period = 60 * 60 * 24  # 24 hours, 60*24 minutes, 60*24*60 seconds.
            w = 2*np.pi/period
            return 21+5*np.cos((t-0)*w)
        else:
            return 27
    else:
        if method == "24hour":
            period = 60 * 60 * 24  # 24 hours, 60*24 minutes, 60*24*60 seconds.
            w = 2*np.pi/period
            return 21+5*np.cos((tank_time-0)*w)
        else:
            return 27


# example 2
def SelfHeatingTank():
    """
    Stepping up from the direct process value control, this example adds in an abstraction layer.

    Instead of the control being in the same space as the target value, the

    The can temperature is
    maintained by a cooler which will have it's control parameter modified based on the output of the PID

    For the tank we'll now use options for:
        Heating rate (C/s) for an internal heater
        Periodic disturbance that temporarily increases the strength of the internal heater.

    For the cooler we'll now use options for:
        for the minimum and maximum rates of cooling based on the process variable

    We will also make use of a 24hour cycle for setting the temperature target. This is to simulate cooling the tank
        to ambient external temperature that changes over the course of the day.
    """

    def ProcessFunction(cooler_param) -> float:
        """
        Internal function
        Connects the cooler to the tank and returns the current temperature. Necessary for PID controller.

        :param cooler_param:
        :return:
        """

        cooler.set_cooler_param(cooler_param)
        can.set_external_heat(cooler.get_cooling_rate())
        can.update_temperature()

        return can.get_temperature()


    print_to_console = False

    # Object setup
    target_temperature = GetTargetTemperature(method="24hour")

    can = TankMonitor.CanOfSoda()
    cooler = TankCooler.Cooler()

    controller = PID.Controller(Kp=10.0, Ki=15.0, Kd=15.0, setpoint=target_temperature)
    controller.conditional_integration = True

    # initial conditions
    process_val = 0

    cooler.set_cooler_param(process_val)
    cooler.min_cool = 3/60
    cooler.max_cool = 7/60

    can.set_external_heat(cooler.get_cooling_rate())
    can.temperature = 48
    can.internal_heater = 4/60
    can.include_disturbance = False

    # set up time array and iteration params
    dt = 1
    t_end = 60*60*24  # seconds
    time_array = np.arange(0, t_end+dt, dt)
    controller.step_size = dt

    # tracking arrays
    cooler_vals = []
    target_vals = []


    # control loop
    for t in time_array:
        controller.setpoint = GetTargetTemperature(t=t)
        current_temp = ProcessFunction(cooler_param=process_val)
        control = controller.calc(process_var=current_temp)

        # We need to back out the control_param from the control output.
        # If control is positive, that means the system is hotter than the target, therefore we need
        #   to increase the speed of the pump (process_val -= 0.1)
        # if the control is negative, that means the system is cooler than the target, therefore we need to
        #   slow down the pump. (process_val += 0.1)
        # because the error is calculated by reference to the measured value (temp) we cannot shove the mechanism
        # control variable into the PID, the domains are different.

        # I'm trying not to overthink it here, but I could pass the ProcessFunction into the controller and have
        # a controller parameter that switches between direct process_var and abstracted method_var...

        if control > 0:
            process_val -= 0.1
            if process_val > cooler.param_range[1]:
                process_val = cooler.param_range[1]
        else:
            process_val += 0.1
            if process_val < cooler.param_range[0]:
                process_val = cooler.param_range[0]

        if print_to_console:
            system_error = control - current_temp
            print(f">>> Control out: {control}\n"
                  f">>> Process out: {current_temp}\n"
                  f">>> System Error: {system_error}\n"
                  f">>> process_val: {process_val}")

        target_vals.append(GetTargetTemperature(t=t))
        cooler_vals.append(process_val)

    temp_history = can.temperature_history
    plt.style.use("bmh")

    fig, ax = plt.subplots(layout="constrained", figsize=(3 * 3, 2 * 3))

    ax.plot(time_array, temp_history, label='System Temperature', color="b")
    ax.plot(time_array, target_vals, color='r', linestyle='--', label=f"Target Temperature")
    ax.set_xlabel("Time(s)")
    ax.set_ylabel("Temperature (C)")
    ax.set_title("PID Controller Simulation \n Heated Can")

    plt.legend()
    plt.show()

# example 3
def LiveSystem():
    """

    This example steps up from example 2 by having the TankMonitor run in real time, have a time delay between gauge
    readings, and automatically adjusts the gain variables

    :return:
    """

    def ProcessFunction(cooler_param) -> float:
        """

        internal function for connecting the cooler to the tank and returning the current temperature. Necessary for PID
        controller.


        :param cooler_param:
        :return:
        """

        cooler.set_cooler_param(cooler_param)
        with lock:
            can.set_external_heat(cooler.get_cooling_rate())
            ret_val = can.get_temperature()

        return ret_val

    def StartVisualMonitor():
        """

        Starts the interactive plotting.

        :return: figure and axis for reference.
        """
        matplotlib.use('TkAgg')
        plt.ion()
        plt.style.use("bmh")
        _fig, _ax = plt.subplots(figsize=(3*3, 2*3))
        _ax.set_xlabel("Time(s)")
        _ax.set_ylabel("Temperature (C)")
        _ax.set_title("PID Controller Simulation \n Heated Can (monitored)")



        plt.show()

        return _fig, _ax

    def UpdateVisualMonitor(data_dict):
        """

        Updates the potting figure with monitor information

        :param data_dict: dictionary containing the data to plot
        :return:
        """

        t_array = data_dict["time_array"]
        temperature_array = data_dict["temp_history"]
        target_values = data_dict["target_vals"]

        ax.clear()

        ax.plot(t_array, temperature_array, color="b",
                label=f'System Temperature: {temperature_array[-1]:0.1f}$\degree$C')

        ax.plot(t_array, target_values, color='g', linestyle='--',
                label=f"Target Temperature: {target_values[-1]:0.1f}$\degree$C")

        ax.axhline(data_dict['critical temp'], color='r', linestyle='--',
                   label=f"Critical Temperature: {data_dict['critical temp']:0.1f}$\degree$C")

        ax.axhspan(data_dict['critical temp']*0.75, data_dict['critical temp']*1.10, color='r', alpha=0.25)

        ax.autoscale_view()


        ax.set_xlabel("Time(s)")
        ax.set_ylabel("Temperature (C)")
        ax.set_title("PID Controller Simulation \n Heated Can (monitored) with Cooler")


        plt.legend(loc="upper left")
        fig.canvas.draw()
        fig.canvas.flush_events()

    def launch_tankmonitor():
        can.run()

    target_temperature = GetTargetTemperature(method="24hour")

    can = TankMonitor.CanOfSoda()
    cooler = TankCooler.Cooler()

    controller = PID.Controller(Kp=20.0, Ki=5.0, Kd=0.5, setpoint=target_temperature)
    controller.conditional_integration = True
    controller.bounds = [-10, 10]
    controller.bound_control = True


    # initial conditions
    process_val = 48
    dt = 1

    cooler.set_cooler_param(process_val)
    cooler.min_cool = 40.0 / 60.0
    cooler.max_cool = 80.0 / 60.0
    cooler.toggle_debug()


    can.set_external_heat(cooler.get_cooling_rate())
    can.temperature = process_val
    can.internal_heater = 50.0 / 60.0
    can.dt = dt
    can.include_disturbance = False

    # tracking arrays
    cooler_vals = []
    target_vals = []
    temperature_vals = []
    time_array = []

    # setup threading
    lock = threading.Lock()
    MonitorThread = threading.Thread(target=launch_tankmonitor, daemon=True)
    MonitorThread.start()

    # setup monitor figure
    fig, ax = StartVisualMonitor()

    initial_step = True

    # control loop
    while True:
        with lock:
            TankReadings = can.GetLiveReading()
            TankTemperature = TankReadings["temperature"]
        if np.isnan(TankTemperature):
            # We are between sample points, we need to let the TankMonitor operate
            time.sleep(can.dt)
        else:
            # we are at the sample point, we can obtain the current_temperature, and apply control corrections.
            _target_temp = GetTargetTemperature(tank_time=TankReadings["time"].second)
            controller.setpoint = _target_temp
            current_temp = ProcessFunction(cooler_param=process_val)
            control = controller.calc(process_var=current_temp)

            # We need to back out the control_param from the control output.
            # If control is positive, that means the system is hotter than the target, therefore we need
            #   to increase the speed of the pump (process_val -= 0.1)
            # if the control is negative, that means the system is cooler than the target, therefore we need to
            #   slow down the pump. (process_val += 0.1)
            # because the error is calculated by reference to the measured value (temp) we cannot shove the mechanism
            # control variable into the PID, the domains are different.

            # I'm trying not to overthink it here, but I could pass the ProcessFunction into the controller and have
            # a controller parameter that switches between direct process_var and abstracted method_var...

            if control < 0:
                print(f"control implies over temp, increasing strength of heat transfer: {control}")
                process_val += 0.1
                if process_val > cooler.param_range[1]:
                    process_val = cooler.param_range[1]
            else:
                print(f"control implies under temp, decreasing strength of heat transfer: {control}")
                process_val -= 0.1  # realistically values should be tied to the magintude of the control var
                if process_val < cooler.param_range[0]:
                    process_val = cooler.param_range[0]


            # update trackers
            target_vals.append(_target_temp)
            cooler_vals.append(process_val)
            temperature_vals.append(current_temp)

            if initial_step:
                time_array.append(dt)
                initial_step = False
            else:
                time_array.append(time_array[-1]+dt)


            plot_dict = {
                "time_array": time_array,
                "temp_history": temperature_vals,
                "target_vals": target_vals,
                "cooler_vals": cooler_vals,
                "critical temp": TankReadings["critical temp"]
            }


            # update figure
            UpdateVisualMonitor(data_dict=plot_dict)



LiveSystem()

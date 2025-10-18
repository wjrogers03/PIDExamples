from utils import dprinter

class Controller:
    def __init__(self, Kp, Ki, Kd, setpoint, GainEvolution=False):
        """
        A simple PID controller. To disable a contributing control term (such as Kp) set the parameter to 0.

        (i.e. if you only want a PI controller, set D = 0)

        :param Kp: Proportional control constant, adjusts to the current error (error(t))
        :param Ki: Integral control constant, adjusts to the cumulative error over time.
        :param Kd: Derivative control constant, adjusts based on predicted errors based on rate of change of error.
        :param setpoint: Desired target value
        :param GainEvolution: If True attempts to modify gain values (not implemented...)
        """

        self.Kp, self.Ki, self.Kd, self.setpoint = Kp, Ki, Kd, setpoint


        self.previous_error = 0
        self.integral = 0

        self.historical_error_size = 10

        self.bounds = [0, 1]
        self.bound_control = False
        self.conditional_integration = False

        self.step_size = 0.01
        self.debug = False
        self.dprinter = dprinter(self.debug)
        self.print = self.dprinter.print
        """
        Iterator step size. Often dt for time, left as step_size to be application agnostic.
        """

    def toggle_debug(self):
        self.debug = not self.debug
        self.dprinter.debug = self.debug

    @staticmethod
    def explain_PID():
        primer = """

                The PID functions by finding the error, cumulative error, and prediction of future error to calculate
                the difference between the setpoint value and the process value. The setpoint value is a predetermined
                end state, such as  motor velocity, temperature, vessel pressure, or other gauge reading. The process\
                value is the current reading of a gauge under current conditions.
                
                The three error source referenced above are:
                
                Proportional Error
                    Defined as the difference between the target value (setpoint) and the current value (process error).
                    This is the largest control knob of the system and should be tuned first during setup.
                
                Integrated Error
                    Defined as the cumulative sum of the the previous errors.
                    
                Differential Error
                    Defined as the rate of change over time between the current error and the previous error. 

                The controller will return the sum of all of these sources of error. 
            
            
                To use the PID, we will need to have:
                1. A target value
                2. A gauge which produces a value based on inputs.
                3. A loop which will adjust the current process variable based on the output of the PID calculation.
                
                Ex:
                //
                def GetTargetPressure() --> float
                def GetSystemPressure(var) --> float
                
                controller = PID.controller()
                controller.step_size = 0.001 #s
                controller.setpoint = GetTargetPressure()
                
                process_variable = 10
                
                for t in time_array:
                    controller_output = controller.calc(process_var = process_variable)
                    process_variable += controller_output*dt - GetSystemPressure(var=process_variable)*dt
                    
                print(f"after {time_array[-1]} the PID found the paramter values of {process_variable} which produces a
                pressure of {GetSystemPressure(var=process_variable)} while target a pressure of {GetTargetPressure()}"
                
                //
                The var provided to the system pressure could be a control that changes the strength of a heater on a
                canister, or controls a pump's flow rate into a cooling apparatus.
                """
        print(primer)

    def calc(self, process_var) -> float:
        """
        Calculates individual control components (Up,Ui,Ud) and sums them, records previous error.

        if conditional_integration (class var) then the process will turn on and off Ui contribtion depending on
        magnitude of error to prevent overshoot.


        :param process_var: value which will be comparred to the setpoint for comparison.
        :return:
        """

        error = self.setpoint - process_var


        # Calculate Proportional error
        Up = self.Kp * error


        # Calculate Integral of error
        do_integration = True

        if self.conditional_integration:
            """
            Conditional integration is a method of addressing integral overshoot until the proportional hammer has
            brought the error back into line.
            """
            if not abs(error) > self.setpoint*0.25:
                do_integration = False
                self.integral = 0 # reset the integral

        if do_integration:
            # Oi = self.Ki
            self.integral = self.integral + error * self.step_size


        Ui = self.Ki * self.integral


        # Calculate Derivative of error
        derivative  = (error-self.previous_error) / self.step_size
        Ud = self.Kd * derivative

        output = Up+Ui+Ud

        self.previous_error = error

        if self.bound_control:
            if output > self.bounds[1]:
                output = self.bounds[1]
            elif output < self.bounds[0]:
                output = self.bounds[0]

        self.print(f">>Error: {error}")
        self.print(f">>Gain: Kp {self.Kp} Ki {self.Ki} Kd {self.Kd}")

        self.print(f">>Adding (P)orportional control: {Up}")
        self.print(f">>Adding (I)ntegral control: {Ui}")
        self.print(f">>Adding (D)erivative control: {Ud}")

        self.print(f"Control Output U = {output}")

        return output

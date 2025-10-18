This repo contains two examples with different degrees of complexity.

BasicExample.py
  A simple PID feedback control system where the process temperature is tuned to a setpoint temperature.

ResponsiveExample.py
  In this example a self heating tank and cooling device is simulated and the control loop monitors the temperature of the tank, and adjusts the parameters of the cooler to maintain tanks temperature at a fixed setpoint.
  While the tank is being monitored a figure is updated in real time.

  This example was created as I wanted to further investigate how a PID works in a more realistice, live monitoring system with multiple components. 


To Run:
  All python was written to function with the most recent version (3.9), but should function with older versions as long as documentation and type hints do not raise errors with the interpreter.

Command Line:
  from the directory containing the files evoke the equivalent of 'python3.9 BasicExample.py'.
From IDE:
  Run as you would your own code.

Python Requirements:
  numpy, time, datetime
  

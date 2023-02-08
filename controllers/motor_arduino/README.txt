
I think the best thing to to is have a Pi Pico connected to the Pi 3 via USB. The Pi 3 will send high-level commands to the pico via a serial connection, and the Pico will handle the low-level stuff. This will free up the pins on the Pi 3, since each motor will require 5 pins to control (Stop, Brake, Direction, Throttle, Speed reporting). I can also use the Pico to handle the PID feedback loop, reducing the load on the main computer. 

https://github.com/PowerBroker2/ArduPID
Use this to handle PID stuff. That can target a speed, rather than a naked throttle value.
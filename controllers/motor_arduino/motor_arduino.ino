#include "speed_monitor.h"
// #include "ArduPID.h"

// ArduPID myController;

int throttle_pin = 3;       // Motor throttle PWM pin
double target_speed = 500;  // Target speed, in cm/s
double throttle;            // Input PWM (i.e. controller input)
double cur_speed;           // Current speed, in m/s

// https://pidexplained.com/how-to-tune-a-pid-controller/
double p = 1;
double i = 0;
double d = 0;


int speed_pin = 2;                              // This pin sees a state change as the wheel turns
unsigned long pulse_timeout = 100000;           // If no pulses for this long, purge the running average (us)
float wheel_diam = 14.0;                        // cm

SpeedMonitor motor_speed(speed_pin, pulse_timeout, wheel_diam);

// Printing variables
unsigned long last_report_time;
int report_period = 100; // milliseconds


void setup()
{
    Serial.begin(115200);
    // Wait for the serial connection to establish. Hacky, but hey ho.
    delay(1000);

    last_report_time = millis();

    // Start a PID controller
    myController.begin(&throttle, &cur_speed, &target_speed, p, i, d);

    myController.setSampleTime(100);       // OPTIONAL - will ensure at least N ms have past between successful compute() calls
    myController.setOutputLimits(0, 255);
    myController.setWindUpLimits(-10, 10); // Groth bounds for the integral term to prevent integral wind-up
}


void loop()
{
    // Poll the motor speed controller
    motor_speed.monitor();

    // If enough time has passed, report the current motor speed
    if (millis() - last_report_time > report_period) 
    {
        Serial.print("Target Speed: ");
        Serial.print(target_speed);
        Serial.println(" cm/s");
        Serial.print("Pulse Frequency: ");
        Serial.print(motor_speed.frequency());
        Serial.println(" Hz");
        Serial.print("Speed: ");
        Serial.print(motor_speed.speed());
        Serial.println(" cm/s");
        Serial.println("");
        last_report_time = millis();
    }

    myController.compute();
    myController.debug(&Serial, "myController", PRINT_INPUT    | // Can include or comment out any of these terms to print
                                                PRINT_OUTPUT   | // in the Serial plotter
                                                PRINT_SETPOINT |
                                                PRINT_BIAS     |
                                                PRINT_P        |
                                                PRINT_I        |
                                                PRINT_D);

    analogWrite(3, throttle); // Replace with plant control signal
}
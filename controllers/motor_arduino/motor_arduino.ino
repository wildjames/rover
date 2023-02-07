#include "speed_monitor.h"
// #include "ArduPID.h"

// ArduPID myController;

// double target_speed = 512; // Target speed, in m/s
// double throttle;           // Input PWM (i.e. controller input)
// double cur_speed;          // Current speed, in m/s
// double p = 1;
// double i = 0;
// double d = 0;


// #define NUM_PULSE_SAMPLES 50
int speed_pin = 2;                              // This pin sees a state change as the wheel turns
unsigned long pulse_timeout = 100000;           // If no pulses for this long, purge the running average (us)
float wheel_diam = 14.0;                        // cm

SpeedMonitor motor_speed(speed_pin, pulse_timeout, wheel_diam);

// Printing variables
unsigned long last_report_time;
int report_period = 1000; // milliseconds

// I have a pulse running on this pin
int test_pin = 3;
int test_pulse_duration = 16700; // microseconds
int last_test_change;


void setup()
{
    Serial.begin(115200);
    // Wait for the serial connection to establish. Hacky, but hey ho.
    delay(1000);

    last_report_time = millis();

    // set up the test PWM pin
    pinMode(test_pin, OUTPUT);
    digitalWrite(test_pin, LOW);
    last_test_change = micros();

    // Start a PID controller
    // myController.begin(&throttle, &cur_speed, &target_speed, p, i, d);

    // myController.setSampleTime(100);       // OPTIONAL - will ensure at least N ms have past between successful compute() calls
    // myController.setOutputLimits(0, 255);
    // myController.setWindUpLimits(-10, 10); // Groth bounds for the integral term to prevent integral wind-up
}



void toggle_test_pin() 
{
    if (micros() - last_test_change > test_pulse_duration)
    {
        if (digitalRead(test_pin)) {
          digitalWrite(test_pin, LOW);
        }
        else {
          digitalWrite(test_pin, HIGH);
        }
        last_test_change = micros();
    }
}



void loop()
{
    motor_speed.monitor();

    toggle_test_pin();

    if (millis() - last_report_time > report_period) 
    {
        Serial.print(motor_speed.average_pulse_duration());
        Serial.println(" us");
        Serial.print(motor_speed.frequency());
        Serial.println(" Hz");
        Serial.print(motor_speed.speed());
        Serial.println(" cm/s");
        Serial.println("");
        last_report_time = millis();
    }

    // myController.compute();
    // myController.debug(&Serial, "myController", PRINT_INPUT    | // Can include or comment out any of these terms to print
    //                                             PRINT_OUTPUT   | // in the Serial plotter
    //                                             PRINT_SETPOINT |
    //                                             PRINT_BIAS     |
    //                                             PRINT_P        |
    //                                             PRINT_I        |
    //                                             PRINT_D);

    // analogWrite(3, throttle); // Replace with plant control signal
}
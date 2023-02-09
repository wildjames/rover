#include "motor_controller.h"
#include "string.h"


/* -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= */
/* -=-=-=-=-=-=-=-=-=-=-=-=-= User Config -=-=-=-=-=-=-=-=-=-=-=-=-=- */
/* -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= */
// https://github.com/jackw01/arduino-pid-autotuner

// Printing variables
int report_period = 10;  // milliseconds

#define NUM_MOTORS 1

// Speed monitoring configurations.
int speed_pins[NUM_MOTORS] = { 2 };                     // This pin sees a state change as the wheel turns
unsigned long pulse_timeouts[NUM_MOTORS] = { 100000 };  // If no pulses for this long (us), purge the running average and set frequency to inf
float wheel_diams[NUM_MOTORS] = { 14.0 };               // cm
int pulses_per_turns[NUM_MOTORS] = { 90 };              // The number of times the speed pin changes state, per wheel revolution

// Motor control variables
int throttle_pins[NUM_MOTORS] = { 3 };  // Motor throttle PWM pin

// https://pidexplained.com/how-to-tune-a-pid-controller/
double p_values[NUM_MOTORS] = { 5.0 };
double i_values[NUM_MOTORS] = { 0.0 };
double d_values[NUM_MOTORS] = { 0.0 };


/* -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= */
/* -=-=-=-=-=-=-=-=-=-=-=- End of User Config -=-=-=-=-=-=-=-=-=-=-=- */
/* -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= */

// Array of motor controlling classes
MotorController* motor_objects[NUM_MOTORS];

// Record last reporting time
unsigned long last_report_time;


void setup() {
  Serial.begin(115200);

  last_report_time = millis();

  for (int i = 0; i < NUM_MOTORS; i++) {
    // motor_speed_monitors[i] = new SpeedMonitor(speed_pins[i], pulse_timeouts[i], wheel_diams[i]);

    // These objects will handle all the motor code
    motor_objects[i] = new MotorController("Motor1",
                                           speed_pins[i],
                                           wheel_diams[i],
                                           pulses_per_turns[i],
                                           throttle_pins[i],
                                           p_values[i],
                                           i_values[i],
                                           d_values[i]);

    motor_objects[i]->report_period = report_period;
    motor_objects[i]->speed_monitor->pulse_timeout = pulse_timeouts[i];
  }
}


void check_serial() {
  // Checks for a command on the Serial connection
  // Commands follow the format:
  // "<motor ID>:<speed>"
  // Multiple commands can be given, delimited by an "&", e.g.
  // "<motor ID>:<speed>&<motor ID>:<speed>"
  // Up to 32 characters can be recieved at once. ID: 1 char, ":": 1 char, speed: 5 chars, "&": 1 char.
  if (Serial.available() > 0) {
    char input[32];
    int available_bytes = Serial.available();
    for (int i = 0; i < available_bytes; i++) {
      input[i] = Serial.read();
    }

    // Read each command pair
    char* command = strtok(input, "&");
    while (command != 0) {
      // Split the command in two values
      char* separator = strchr(command, ':');
      if (separator != 0) {
        // Actually split the string in 2: replace ':' with 0
        *separator = 0;
        int motorId = atoi(command);
        ++separator;
        int position = atoi(separator);

        motor_objects[motorId]->target_speed = position;
      }
      // Find the next command in input string
      command = strtok(0, "&");
    }
  }
}


void loop() {
  // Update the motors
  for (int i = 0; i < NUM_MOTORS; i++) {
    motor_objects[i]->loop();
  }

  // Check for commands
  check_serial();
}
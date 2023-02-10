#include "motor_controller.h"
#include "ArduPID.h"
#include "Strings.h"


MotorController::MotorController(char* name,
                                 int speed_pin,
                                 int brake_pin,
                                 int dir_pin,
                                 float wheel_diameter_cm,
                                 int pulses_per_turn,
                                 int throttle_pin,
                                 const double& p,
                                 const double& i,
                                 const double& d) {

  _name = name;

  // Create the speed monitor object
  speed_monitor = new SpeedMonitor(speed_pin, wheel_diameter_cm, pulses_per_turn);

  // Create the PID controller
  PID = new ArduPID();
  PID->begin(&cur_speed, &throttle, &target_speed, p, i, d);

  // PID controller config.
  PID->setSampleTime(PID_sample_time);  // OPTIONAL - will ensure at least N ms have past between successful compute() calls
  PID->setOutputLimits(0, 255);         // Impose limits on the output values. PWM duty cycle
  // PID->setWindUpLimits(-50, 50);      // Groth bounds for the integral term to prevent integral wind-up

  // The PID needs to be started before compute does anything
  PID->start();

  // PWM output
  _throttle_pin = throttle_pin;
  _brake_pin = brake_pin;
  _dir_pin = dir_pin;

  pinMode(_throttle_pin, OUTPUT);
  analogWrite(_throttle_pin, 0);

  pinMode(_brake_pin, OUTPUT);
  digitalWrite(_brake_pin, LOW);

  pinMode(_dir_pin, OUTPUT);
  digitalWrite(_dir_pin, LOW);

  // Some times to be tracked
  last_report_time = millis();
  last_speed_update = millis();
};


void MotorController::loop() {
  speed_monitor->monitor();

  if (millis() - last_speed_update > speed_poll_time) {
    cur_speed = speed_monitor->speed();
    last_speed_update = millis();
  }

  if (active_deceleration) 
  {
    if ((target_speed < cur_speed) && (!brake_state)) brake(1);
    else brake(0);
  }

  // This has a built-in timer
  PID->compute();

  // Update the pin on each loop, it is fast
  analogWrite(_throttle_pin, throttle);

  // If enough time has passed, report the current motor speed
  if (millis() - last_report_time > report_period) {
    // PID->debug(&Serial, _name, PRINT_INPUT | PRINT_OUTPUT | PRINT_SETPOINT);
    // Serial.print("Target: ");
    Serial.print(target_speed);
    Serial.print("\t");
    // Serial.print("Current: ");
    Serial.print(speed_monitor->speed());
    Serial.print("\t");
    // Serial.print("Throttle: ");
    Serial.print(map(throttle, 0, 255, 0, 100));
    Serial.println("");

    last_report_time = millis();
  }
}


void MotorController::reverse(int enabled)
// Set the direction to forwards or backwards
{
  if (enabled) digitalWrite(_dir_pin, HIGH);
  else digitalWrite(_dir_pin, LOW);
  reverse_state = enabled;

  return;
}


void MotorController::brake(int enabled)
// Set the state of the brake
{
  if (enabled) digitalWrite(_brake_pin, HIGH);
  else digitalWrite(_brake_pin, LOW);
  brake_state = enabled;

  return;
}


float MotorController::speed() {
  // Just alias the speed monitor function
  return speed_monitor->speed();
}

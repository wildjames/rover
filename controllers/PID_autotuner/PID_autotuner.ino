#include "speed_monitor.h"
#include <pidautotuner.h>

// GPIO pins
int speed_pin = 2;
int throttle_pin = 3;

double throttle = 0;
double speed = 0.0;
double setpoint = 100.0;

// this must be updated as often as possible
SpeedMonitor speed_monitor(speed_pin, 14.0, 90.0);

// Time between PID tuner updates
int loopInterval = 100000;


void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting");

  pinMode(throttle_pin, OUTPUT);

  PIDAutotuner tuner = PIDAutotuner();

  // Set the target value to tune to
  // This will depend on what you are tuning. This should be set to a value within
  // the usual range of the setpoint. For low-inertia systems, values at the lower
  // end of this range usually give better results. For anything else, start with a
  // value at the middle of the range.
  tuner.setTargetInputValue(setpoint);

  // Set the loop interval in microseconds
  // This must be the same as the interval the PID control loop will run at
  tuner.setLoopInterval(loopInterval);

  // Set the output range
  // These are the minimum and maximum possible output values of whatever you are
  // using to control the system (Arduino analogWrite, for example, is 0-255)
  tuner.setOutputRange(0, 255);

  // Set the Ziegler-Nichols tuning mode
  // Set it to either PIDAutotuner::ZNModeBasicPID, PIDAutotuner::ZNModeLessOvershoot,
  // or PIDAutotuner::ZNModeNoOvershoot. Defaults to ZNModeNoOvershoot as it is the
  // safest option.
  tuner.setZNMode(PIDAutotuner::ZNModeLessOvershoot);

  // This must be called immediately before the tuning loop
  // Must be called with the current time in microseconds
  tuner.startTuningLoop(micros());

  // Run a loop until tuner.isFinished() returns true
  long microseconds;
  while (!tuner.isFinished()) {

    // This loop must run at the same speed as the PID control loop being tuned
    long prevMicroseconds = microseconds;
    microseconds = micros();

    // Get current_speed value here (temperature, encoder position, velocity, etc)
    double current_speed = speed_monitor.speed();

    // Call tunePID() with the current_speed value and current time in microseconds
    double throttle = tuner.tunePID(current_speed, microseconds);

    // Set the throttle - tunePid() will return values within the range configured
    // by setOutputRange(). Don't change the value or the tuning results will be
    // incorrect.
    analogWrite(throttle_pin, throttle);

    // This loop must run at the same speed as the PID control loop being tuned
    while (micros() - microseconds < loopInterval) {
      speed_monitor.monitor();
    }
  }

  // Turn the output off here.
  analogWrite(throttle_pin, 0);

  // Get PID gains - set your PID controller's gains to these
  double kp = tuner.getKp();
  double ki = tuner.getKi();
  double kd = tuner.getKd();

  Serial.print("P: ");
  Serial.println(kp);
  Serial.print("I: ");
  Serial.println(ki);
  Serial.print("D: ");
  Serial.println(kd);
}

void loop() {

  // ...
}
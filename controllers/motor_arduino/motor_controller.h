#ifndef MotorController_h
#define MotorController_h

#include "speed_monitor.h"
#include "ArduPID.h"


class MotorController {

public:
  MotorController(
    char* name,
    int speed_pin,
    int brake_pin,
    int dir_pin,
    float wheel_diameter_cm,
    int pulses_per_turn,
    int throttle_pin,
    const double& p = 0,
    const double& i = 0,
    const double& d = 0);

  void loop();
  float speed();

  void reverse(int enabled);
  void brake(int enabled);

  int brake_state = 1;
  int reverse_state = 0;

  double target_speed = 0;    // Target speed, in cm/s
  int speed_poll_time = 10;   // Speed we be recalculated every N ms
  int PID_sample_time = 25;   // ms
  int report_period = 10000;  // ms

  // If this is enabled, then whenever the actual speed is higher 
  // than the target speed, the brakes will be applied.
  bool active_deceleration = false;

  // My speed monitor object
  SpeedMonitor* speed_monitor;

private:
  char* _name;

  ArduPID* PID;

  double throttle;       // Output PWM (i.e. controller input)
  double cur_speed = 0;  // The current speed.

  int _throttle_pin;
  int _brake_pin;
  int _dir_pin;

  int last_speed_update;

  // Record last reporting time
  unsigned long last_report_time;
};

#endif

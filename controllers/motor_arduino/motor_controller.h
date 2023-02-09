#ifndef MotorController_h
#define MotorController_h

#include "speed_monitor.h"
#include "ArduPID.h"


class MotorController {

public:
  MotorController(
    char* name,
    int speed_pin,
    float wheel_diameter_cm,
    int pulses_per_turn,
    int throttle_pin,
    const double& p = 0,
    const double& i = 0,
    const double& d = 0);

  void loop();
  float speed();


  double target_speed = 0;  // Target speed, in cm/s

  int speed_poll_time = 100;   // Speed we be recalculated every N ms
  int report_period = 10000;  // milliseconds

  // Class functions
  SpeedMonitor* speed_monitor;

private:
  char* _name;

  ArduPID* PID;

  double throttle;       // Output PWM (i.e. controller input)
  double cur_speed = 0;  // The current speed.

  int _throttle_pin;
  // RP2040_PWM* throttle_pwm;

  int last_speed_update;

  // Record last reporting time
  unsigned long last_report_time;
};

#endif

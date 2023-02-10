#ifndef SpeedMonitor_h
#define SpeedMonitor_h

#include "Arduino.h"

#ifndef NUM_PULSE_SAMPLES
#define NUM_PULSE_SAMPLES 50
#endif

#ifndef PI
#define PI 3.14159
#endif


class SpeedMonitor {

public:
  SpeedMonitor(int speed_input_pin, float wheel_diameter, int pulses_per_turn);
  
  void monitor();

  double average_pulse_duration();
  float frequency();
  float speed();

  unsigned long pulse_timeout = 100000;  // If no pulses for this long, purge the running average (us)
  unsigned long pulse_count = 0;

private:
  int _speed_pin;      // This pin sees a state change as the wheel turns
  float _wheel_diameter;  // The diameter of the wheel, duh
  int _pulses_per_turn;

  unsigned long last_speed_pin_change;  // Time of last change in the speed pin
  uint8_t last_speed_pin_state;         // Last state of the speed pin

  unsigned long speed_pulse_durations[NUM_PULSE_SAMPLES] = { 0 };  // Array of times of the last N speed pin changes
};

#endif

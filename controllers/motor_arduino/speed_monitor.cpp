#include <Arduino.h>
#include "speed_monitor.h"

SpeedMonitor::SpeedMonitor(int speed_input_pin, float wheel_diameter_cm, int pulses_per_turn) {
  _speed_pin = speed_input_pin;
  _wheel_diameter = wheel_diameter_cm;
  _pulses_per_turn = pulses_per_turn;

  // Set up the speed pin
  pinMode(_speed_pin, INPUT);
  last_speed_pin_state = digitalRead(_speed_pin);
  last_speed_pin_change = micros();
};


void SpeedMonitor::monitor() {
  unsigned long timenow = micros();
  if (digitalRead(_speed_pin) != last_speed_pin_state) {
    // Shift the array of pulse durations along
    for (int i = NUM_PULSE_SAMPLES - 1; i > 0; i--) {
      speed_pulse_durations[i] = speed_pulse_durations[i - 1];
    }
    // store the new value
    speed_pulse_durations[0] = timenow - last_speed_pin_change;

    // Then set the new last speed pin state ASAP
    last_speed_pin_change = timenow;
    last_speed_pin_state = digitalRead(_speed_pin);

    // And count the pulses
    pulse_count++;
  } else {
    if (timenow - last_speed_pin_change > pulse_timeout) {
      for (int i = 0; i < NUM_PULSE_SAMPLES; i++) {
        speed_pulse_durations[i] = 0;
      }
    }
  }
};


double SpeedMonitor::average_pulse_duration() {
  // And calculate the average pulse duration
  double pulse_dur = 0;
  int num_samples = 0;
  for (int i = 0; i < NUM_PULSE_SAMPLES; i++) {
    pulse_dur += speed_pulse_durations[i];
    if (speed_pulse_durations[i] != 0) {
      num_samples++;
    }
  }
  if (pulse_dur != 0 & num_samples > 5) {
    pulse_dur /= num_samples;
  }

  return pulse_dur;
};


float SpeedMonitor::frequency() {
  float pulse_dur = average_pulse_duration();
  if (pulse_dur == 0) {
    return 0.0;
  }
  return 1000000.0 / (pulse_dur * _pulses_per_turn);
}


float SpeedMonitor::speed() {
  return PI * _wheel_diameter * frequency();
}

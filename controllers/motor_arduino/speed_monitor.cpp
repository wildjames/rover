#include <Arduino.h>
#include "speed_monitor.h"

SpeedMonitor::SpeedMonitor(int speed_input_pin, unsigned long pulse_timeout_us, float wheel_diameter_cm) {
    speed_pin = speed_input_pin;
    pulse_timeout = pulse_timeout_us;
    _wheel_diameter = wheel_diameter_cm;

    // Set up the speed pin
    pinMode(speed_pin, INPUT);
    last_speed_pin_state = digitalRead(speed_pin);
    last_speed_pin_change = micros();
};

void SpeedMonitor::monitor()
{
    unsigned long timenow = micros();
    if (digitalRead(speed_pin) != last_speed_pin_state)
    {
        // Shift the array of pulse durations along
        for (int i = NUM_PULSE_SAMPLES-1; i > 0; i--)
        {
            speed_pulse_durations[i] = speed_pulse_durations[i-1];
        }
        // store the new value
        speed_pulse_durations[0] = timenow - last_speed_pin_change;

        // Then set the new last speed pin state ASAP
        last_speed_pin_change = timenow;
        last_speed_pin_state = digitalRead(speed_pin);
    }
    else 
    {
        if (timenow - last_speed_pin_change > pulse_timeout)
        {
            for (int i=0; i<NUM_PULSE_SAMPLES; i++)
            {
                speed_pulse_durations[i] = 0;
            }
        }
    }
};


double SpeedMonitor::average_pulse_duration() 
{
    // And calculate the average pulse duration
    double pulse_dur = 0;
    int num_samples = 0;
    for (int i = 0; i < NUM_PULSE_SAMPLES; i++)
    {
        pulse_dur += speed_pulse_durations[i];
        if (speed_pulse_durations[i] != 0) {
          num_samples++;
        }
    }
    if (pulse_dur != 0) 
    {
        pulse_dur /= num_samples;
    }

    return pulse_dur;
};


float SpeedMonitor::frequency() 
{
    float pulse_dur = average_pulse_duration();
    return 1000000 / pulse_dur;
}


float SpeedMonitor::speed()
{
    return PI * _wheel_diameter * frequency();
}


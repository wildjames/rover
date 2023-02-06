// Every N minutes, if the Rpi is not powered on, it is given power.
// If it is no longer running, cut power to it and begin waiting for the next N minute interval.

// **** INCLUDES *****
#include "SleepyPi2.h"
#include <TimeLib.h>
#include <LowPower.h>
#include <PCF8523.h>
#include <Wire.h>

const char *monthName[12] = {
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
};

const int LED_PIN = 13;

DateTime current_time;
int wakeup_hour;
int wakeup_min;

// Globals
// ++++++++++++++++++++ CHANGE ME ++++++++++++++++++
uint8_t          POWOFF_INTERVAL_MIN        = 30;           // Wake up this often, in minutes.
uint32_t         RPI_BOOT_ALLOWANCE         = 30000;        // Time to allow for the Pi to boot - milliseconds
uint32_t         POLL_DELAY_MS              = 10000;        // Check if the Pi is drawing current with this interval while it is on.
// ++++++++++++++++++++ END CHANGE ME ++++++++++++++++++

tmElements_t tm;


void alarm_isr()
{
    // Just a handler for the alarm interrupt.
    // You could do something here

}

void setup()
{ 
  delay(500);
  
  // Configure "Standard" LED pin
  pinMode(LED_PIN, OUTPUT);		
  digitalWrite(LED_PIN,LOW);		// Switch off LED

  // initialize serial communication: In Arduino IDE use "Serial Monitor"
  Serial.begin(9600);
  Serial.println("Starting...");
  delay(50);
  SleepyPi.rtcInit(true);
  
  printTimeNow();   

  Serial.println("Powering on the Pi");
  SleepyPi.enablePiPower(true);

  delay(RPI_BOOT_ALLOWANCE);
}

void loop() 
{
    // Just a few things to show what's happening
    Serial.print("What is the Pi current draw right now? ");
    Serial.print(SleepyPi.rpiCurrent());
    Serial.println(" mA");
    digitalWrite(LED_PIN,HIGH);    // Switch on LED
    
    // Switch on the Pi
    SleepyPi.enablePiPower(true);
    
    Serial.println("I've Just woken up on a Periodic Timer!");
    
    // Print the time
    printTimeNow();

    Serial.println("Waiting for Pi to boot");
    delay(RPI_BOOT_ALLOWANCE);
    
    while (SleepyPi.checkPiStatus(false)) {
        Serial.println("Rpi is running");
        Serial.println("current_draw ");
        Serial.println(SleepyPi.rpiCurrent());
        Serial.print("Handshake Pin: ");
        Serial.println(SleepyPi.checkPiStatus(false));
        
        current_time = SleepyPi.readTime();
        wakeup_hour = current_time.hour();
        wakeup_min = (((current_time.minute() / POWOFF_INTERVAL_MIN) + 1) * POWOFF_INTERVAL_MIN) % 60;
        if (wakeup_min == 0) {
          wakeup_hour = (wakeup_hour + 1) % 24;
        }

        Serial.println("Time is currently: ");
        printTimeNow();
        Serial.print("Next alarm would be at ");
        Serial.print(wakeup_hour);
        Serial.print(":");
        Serial.print(wakeup_min);
        Serial.println("");
    
        Serial.println("Leaving Rpi power on");
        delay(POLL_DELAY_MS);
    }
    
    Serial.println("Rpi is not running");
    Serial.println("Cutting Rpi power");
    for (int i=0; i < 5; i++) {
        digitalWrite(LED_PIN, HIGH);
        delay(500);
        digitalWrite(LED_PIN, LOW);
        delay(500);
    }
    
    SleepyPi.enablePiPower(false);

    // Time to sleep
    SleepyPi.rtcClearInterrupts();

    // Allow wake up alarm to trigger interrupt on falling edge.
    attachInterrupt(0, alarm_isr, FALLING);    // Alarm pin

    // Set the alarm
    SleepyPi.enableWakeupAlarm(true);

    // Read the time
    current_time = SleepyPi.readTime();
    wakeup_hour;
    wakeup_min;
    
    wakeup_hour = current_time.hour();
    wakeup_min = (((current_time.minute() / POWOFF_INTERVAL_MIN) + 1) * POWOFF_INTERVAL_MIN) % 60;

    if (wakeup_min == 0) {
      wakeup_hour = (wakeup_hour + 1) % 24;
    }

    Serial.print("Setting alarm for ");
    Serial.print(wakeup_hour);
    Serial.print(":");
    Serial.print(wakeup_min);
    Serial.println("");
    
    SleepyPi.setAlarm(wakeup_hour, wakeup_min);

    delay(500);

    // Enter power down state with ADC and BOD module disabled.
    // Wake up when wake up pin is low.
    SleepyPi.powerDown(SLEEP_FOREVER, ADC_OFF, BOD_OFF); 

    // Disable external pin interrupt on wake up pin.
    detachInterrupt(0);
    
    SleepyPi.ackAlarm();

}

// **********************************************************************
// 
//  - Helper routines
//
// **********************************************************************

void printTimeNow()
{
    // Read the time
    DateTime now = SleepyPi.readTime();
    
    // Print out the time
    Serial.print("Ok, Time = ");
    print2digits(now.hour());
    Serial.write(':');
    print2digits(now.minute());
    Serial.write(':');
    print2digits(now.second());
    Serial.print(", Date (D/M/Y) = ");
    Serial.print(now.day());
    Serial.write('/');
    Serial.print(now.month()); 
    Serial.write('/');
    Serial.print(now.year(), DEC);
    Serial.println();

    return;
}
bool getTime(const char *str)
{
  int Hour, Min, Sec;

  if (sscanf(str, "%d:%d:%d", &Hour, &Min, &Sec) != 3) return false;
  tm.Hour = Hour;
  tm.Minute = Min;
  tm.Second = Sec;
  return true;
}

bool getDate(const char *str)
{
  char Month[12];
  int Day, Year;
  uint8_t monthIndex;

  if (sscanf(str, "%s %d %d", Month, &Day, &Year) != 3) return false;
  for (monthIndex = 0; monthIndex < 12; monthIndex++) {
    if (strcmp(Month, monthName[monthIndex]) == 0) break;
  }
  if (monthIndex >= 12) return false;
  tm.Day = Day;
  tm.Month = monthIndex + 1;
  tm.Year = CalendarYrToTm(Year);
  return true;
}

void print2digits(int number) {
  if (number >= 0 && number < 10) {
    Serial.write('0');
  }
  Serial.print(number);
}

/*
  IMU Capture
  This sketch uses the on-board IMU to get acceleration and gyroscope values.
  It detects motion state of the Arduino and activates on significant motion.
*/

#include <Arduino.h>
#include <Arduino_BMI270_BMM150.h>
#include "avr/dtostrf.h"
#include "custom_serialcom.h"

#define RED_PIN    22
#define GREEN_PIN  23
#define BLUE_PIN   24
#define YELLOW_PIN LED_BUILTIN
#define NO_PIN     -1

// Globals
namespace {
  char varbuf[128];  // Increased buffer size for combined data
  const float accelerationThreshold = 1.5; // in G's
  const int samples2Read = 20;  // Changed to 20 as per requirements
  int samplesRead = 0;
}

// Helper function to check if IMU data is ready
bool imuDataReady() {
  return IMU.accelerationAvailable() && IMU.gyroscopeAvailable();
}

void setup() {
  if (!IMU.begin()) {
    HandleOutput_error(-1);
    while(1);
  }
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(YELLOW_PIN, OUTPUT);
  double demo_val = HandleInput_double();
  HandleOutput_double(demo_val);
  light_led(NO_PIN);
}

void loop() {
  float aX, aY, aZ, gX, gY, gZ;

  // wait for significant motion
  while (samplesRead < samples2Read) {
    light_led(NO_PIN);
    light_led(GREEN_PIN);
    
    while(1) {
      if (imuDataReady()) {
        // read the data
        IMU.readAcceleration(aX, aY, aZ);
        IMU.readGyroscope(gX, gY, gZ);

        // See if acceleration warrants further processing
        float aSum = fabs(aX) + fabs(aY) + fabs(aZ);
        if (aSum >= accelerationThreshold) break;
      }
    }
    light_led(NO_PIN);

    // Indicate data capture with RED LED
    light_led(RED_PIN);
    
    // Send all IMU data in one message
    HandleOutput_IMU(aX, aY, aZ, gX, gY, gZ);
    
    // Show progress
    HandleOutput_status(samplesRead + 1);
    
    delay(1000);  // Reduced delay for faster data collection
    samplesRead++;
  }

  // Visual indicator for completion - cycle through LEDs
  while(1) {
    light_led(RED_PIN);
    delay(500);
    light_led(GREEN_PIN);
    delay(500);
    light_led(BLUE_PIN);
    delay(500);
    light_led(NO_PIN);
    delay(500);
  }
}


void HandleOutput_IMU(float aX, float aY, float aZ, float gX, float gY, float gZ) {
  // Send values with consistent formatting
  for (float val : {aX, aY, aZ, gX, gY, gZ}) {
    dtostrf(val, 10, 3, varbuf);
    csc_write_data(CSC_CMD_WRITE_PI_LOG, (byte*)varbuf, strlen(varbuf));
  }
}
void HandleOutput_int(int log_int) {
  itoa(log_int, varbuf, 10);
  csc_write_data(CSC_CMD_WRITE_PI_LOG, (byte*)varbuf, strlen(varbuf));
}

void HandleOutput_uint(unsigned int log_int) {
  utoa(log_int, varbuf, 10);
  csc_write_data(CSC_CMD_WRITE_PI_LOG, (byte*)varbuf, strlen(varbuf));
}

void HandleOutput_double(double log_double) {
  dtostrf(log_double, 10, 3, varbuf);
  csc_write_data(CSC_CMD_WRITE_PI_LOG, (byte*)varbuf, strlen(varbuf));
}

void HandleOutput_status(int status) {
  itoa(status, varbuf, 10);
  csc_write_data(CSC_CMD_WRITE_PI_STATUS, (byte*)varbuf, strlen(varbuf));
}

void HandleOutput_error(int error_code) {
  itoa(error_code, varbuf, 10);
  csc_write_data(CSC_CMD_WRITE_PI_ERROR, (byte*)varbuf, strlen(varbuf));
}

double HandleInput_double() {
  int bytes_read = csc_read_data((byte*)varbuf);
  return(atof(varbuf));
}

void light_led(int color) {
  if (color == NO_PIN) { // turn off all the LEDs
    // These pins are asserted low
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, HIGH);
    digitalWrite(BLUE_PIN, HIGH);
    // This pin is asserted high
    digitalWrite(YELLOW_PIN, LOW);
  }
  else { // Turn on the pin you want
    if (color == YELLOW_PIN) {
      digitalWrite(color, HIGH);
    }
    else {
      digitalWrite(color, LOW);
    }
  }
}

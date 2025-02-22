#include <Arduino.h>
#include <Arduino_HS300x.h>  // Temperature sensor library
#include "custom_serialcom.h"

// LED Pin definitions
#define RED_PIN    22   // Higher temp
#define GREEN_PIN  23   // Same temp
#define BLUE_PIN   24   // Lower temp
#define YELLOW_PIN LED_BUILTIN
#define NO_PIN     -1

// Buffer to store temperature readings
float tempBuffer[60];
int tempIndex = 0;
unsigned long lastReadTime = 0;
const unsigned long READ_INTERVAL = 1000; // 1 second interval

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

void setup() {
  // Initialize LED pins
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(YELLOW_PIN, OUTPUT);
  light_led(NO_PIN);
  
  Serial.begin(9600);
  while (!Serial);

  if (!HS300x.begin()) {
    // Send error message using proper protocol
    String error_msg = "Failed to initialize temperature sensor!";
    byte error_buf[64];
    error_msg.getBytes(error_buf, 64);
    csc_write_data(CSC_CMD_WRITE_PI_ERROR, error_buf, error_msg.length());
    while (1); // Stop if sensor initialization fails
  }
}

void loop() {
  unsigned long currentTime = millis();
  
  // Read temperature every second
  if (currentTime - lastReadTime >= READ_INTERVAL) {
    lastReadTime = currentTime;
    
    // Flash yellow to indicate reading
    light_led(YELLOW_PIN);
    delay(100);
    light_led(NO_PIN);
    
    // Read temperature and store in buffer
    float currentTemp = HS300x.readTemperature();
    tempBuffer[tempIndex] = currentTemp;
    
    // Light green LED while collecting data
    light_led(GREEN_PIN);
    
    tempIndex++;
    
    // When buffer is full (60 readings = 1 minute)
    if (tempIndex >= 60) {
      // Calculate average
      float sum = 0;
      for (int i = 0; i < 60; i++) {
        sum += tempBuffer[i];
      }
      float average = sum / 60.0;
      
      // Send data using proper protocol
      String tempMsg = "TEMP:" + String(average, 2);
      byte data_buf[32];
      tempMsg.getBytes(data_buf, 32);
      csc_write_data(CSC_CMD_WRITE_PI_LOG, data_buf, tempMsg.length());
      
      // Reset index for next minute
      tempIndex = 0;
      
      // Indicate data transmission with blue LED
      light_led(BLUE_PIN);
      delay(200);
      light_led(NO_PIN);
    }
    
    delay(100);
    light_led(NO_PIN);
  }
}

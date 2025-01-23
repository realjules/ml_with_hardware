#include <Arduino.h>
#include <Arduino_HS300x.h>  // Changed from HTS221 to HS300x

// For use with the LED
#define RED_PIN    22   // Higher temp
#define GREEN_PIN  23   // Same temp
#define BLUE_PIN   24   // Lower temp
#define YELLOW_PIN LED_BUILTIN
#define NO_PIN     -1

// Globals
float prevTemp = 0.0;
float currTemp = 0.0;
bool firstReading = true;

void setup() {
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(YELLOW_PIN, OUTPUT);
  light_led(NO_PIN);
  
  if (!HS300x.begin()) {  // Changed from HTS to HS300x
    while (1); // Stop if sensor initialization fails
  }
}

void loop() {
  // Flash yellow to indicate reading is about to start
  light_led(YELLOW_PIN);
  delay(250);  // 0.25 seconds
  light_led(NO_PIN);
  
  // Read temperature
  currTemp = HS300x.readTemperature();  // Changed from HTS to HS300x
  
  // Flash yellow again to indicate reading is complete
  light_led(YELLOW_PIN);
  delay(250);  // 0.25 seconds
  light_led(NO_PIN);
  
  // Compare temperatures and light appropriate LED
  if (firstReading) {
    light_led(GREEN_PIN);  // First reading, show green
    firstReading = false;
  } else if (currTemp > prevTemp) {
    light_led(RED_PIN);    // Temperature increased
  } else if (currTemp < prevTemp) {
    light_led(BLUE_PIN);   // Temperature decreased
  } else {
    light_led(GREEN_PIN);  // Temperature unchanged
  }
  
  delay(2500);  // Keep LED on for 2.5 seconds
  light_led(NO_PIN);
  
  prevTemp = currTemp;  // Store current temp for next comparison
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
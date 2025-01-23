#include <Arduino.h>

// For use with the LED
#define RED_PIN    22
#define GREEN_PIN  23
#define BLUE_PIN   24
#define YELLOW_PIN LED_BUILTIN
#define NO_PIN     -1

// Globals
namespace{
  int loop_cnt = 0;
}

void setup(){
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(YELLOW_PIN, OUTPUT);
  light_led(NO_PIN);
}

void loop(){
  if(loop_cnt % 4 == 0){
    light_led(RED_PIN);
    delay(500);  // 0.5 seconds for red
  }
  else if(loop_cnt % 4 == 1){
    light_led(GREEN_PIN);
    delay(750);  // 0.75 seconds for green
  }
  else if(loop_cnt % 4 == 2){
    light_led(BLUE_PIN);
    delay(1000); // 1.0 seconds for blue
  }
  else{
    light_led(YELLOW_PIN);
    delay(100);  // 0.1 seconds for yellow
  }
  
  light_led(NO_PIN);
  delay(500);    // Keep the same gap between LEDs
  loop_cnt++;
}

void light_led(int color){
  if(color == NO_PIN){ // turn off all the LEDs
    // These pins are asserted low
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, HIGH);
    digitalWrite(BLUE_PIN, HIGH);
    // This pin is asserted high 
    digitalWrite(YELLOW_PIN, LOW);
  }
  else{ // Turn on the pin you want
    if(color == YELLOW_PIN){
      digitalWrite(color, HIGH);
    }
    else{
      digitalWrite(color, LOW);
    }
  }
}
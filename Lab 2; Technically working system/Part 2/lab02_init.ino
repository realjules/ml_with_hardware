#include <TensorFlowLite.h>
#include <math.h>
#include <Arduino.h>
#include "avr/dtostrf.h"

#include "main_functions.h"
#include "model.h"
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_log.h"
#include "tensorflow/lite/micro/system_setup.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "custom_serialcom.h"

// For use with the LED
#define RED_PIN    22
#define GREEN_PIN  23
#define BLUE_PIN   24
#define YELLOW_PIN LED_BUILTIN
#define NO_PIN     -1

// Globals
namespace{
  char varbuf[128];

  /* Globals needed for TensorFlow Lite Micro (TFLM) */
  const tflite::Model* tflModel = nullptr;
  tflite::MicroInterpreter* tflInterpreter = nullptr;
  TfLiteTensor* tflInputTensor = nullptr;
  TfLiteTensor* tflOutputTensor = nullptr;
  static tflite::AllOpsResolver tflOpsResolver;

  const int kTensorArenaSize = 2000;
  uint8_t tensorArena[kTensorArenaSize];

  int inference_count = 0;
  // the model was trained to estimate values between 0 and 2*pi
  float kXrange = 2.0 * 3.14159265359;
  float kInferencesPerCycle = 500;
}

// The Arduino calls this once when execution begins
void setup(){
  // Get the TFL representation of the model byte array.
  // Create an interpreter to run the model.
  // Allocate memory to hold the tensors.
  // Get pointers to the tensors.

	tflite::InitializeTarget();
  tflModel = tflite::GetModel(g_model);
  if(tflModel->version() != TFLITE_SCHEMA_VERSION) {
    HandleOutput_error(-100);
    while (1);
  }
  static tflite::MicroInterpreter static_interpreter(tflModel, tflOpsResolver,
                      tensorArena, kTensorArenaSize);
	tflInterpreter = &static_interpreter;
  TfLiteStatus allocate_status = tflInterpreter->AllocateTensors();
	if(allocate_status != kTfLiteOk){
    HandleOutput_error(-101);
		while(1);
	}	

  // Obtain pointers to the model's input and output tensors.
  tflInputTensor = tflInterpreter->input(0);
  tflOutputTensor = tflInterpreter->output(0);

  // Keep track of how many inferences we have performed.
  inference_count = 0;
  light_led(NO_PIN);
}

void HandleOutput_ml(double x, double y) {
    // Format x value with 3 decimal places
    dtostrf(x, 10, 3, varbuf);
    csc_write_data(CSC_CMD_WRITE_PI_MLX, (byte*)varbuf, strlen(varbuf));

    // Format y value with 3 decimal places  
    dtostrf(y, 10, 3, varbuf);
    csc_write_data(CSC_CMD_WRITE_PI_MLY, (byte*)varbuf, strlen(varbuf));
}

void loop() {
    // Calculate x value
    float position = inference_count / kInferencesPerCycle;
    float x = position * kXrange;
    
    // Run inference
    tflInputTensor->data.f[0] = x;
    TfLiteStatus invoke_status = tflInterpreter->Invoke();
    if(invoke_status != kTfLiteOk) {
        HandleOutput_error(-102);
        while(1);
    }

    // Get output value
    float y = tflOutputTensor->data.f[0];

    // Light LED based on y value
    light_led(NO_PIN);
    if(y < 0) light_led(RED_PIN);
    else light_led(GREEN_PIN);

    // Send x and y values
    HandleOutput_ml(x, y); 

    // Increment counter
    inference_count += 1;
    if(inference_count >= kInferencesPerCycle) inference_count = 0;
    
    delay(100);
}

void light_led(int color){
  if( color == NO_PIN ){ // turn off all the LEDs
    // These pins are asserted low
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, HIGH);
    digitalWrite(BLUE_PIN, HIGH);
    // This pin is asserted high
    // (FYI so is the power pin which we don't use)
    digitalWrite(YELLOW_PIN, LOW);
  }
  else{ // Turn on the pin you want
    if( color == YELLOW_PIN){
      digitalWrite(color, HIGH);
    }
    else{
      digitalWrite(color, LOW);
    }
  }
}

// For easy output to RPi
void HandleOutput_int(int log_int){
	itoa(log_int, varbuf, 10);
	csc_write_data(CSC_CMD_WRITE_PI_LOG, (byte*)varbuf, strlen(varbuf) );
}
void HandleOutput_uint(unsigned int log_int){
	utoa(log_int, varbuf, 10);
	csc_write_data(CSC_CMD_WRITE_PI_LOG, (byte*)varbuf, strlen(varbuf) );
}
void HandleOutput_double(double log_double){
	dtostrf(log_double, 10, 3, varbuf);
	csc_write_data(CSC_CMD_WRITE_PI_LOG, (byte*)varbuf, strlen(varbuf) );
}
void HandleOutput_status(int status){
	itoa(status, varbuf, 10);
	csc_write_data(CSC_CMD_WRITE_PI_STATUS, (byte*)varbuf, strlen(varbuf) );
}
void HandleOutput_error(int error_code){
	itoa(error_code, varbuf, 10);
	csc_write_data(CSC_CMD_WRITE_PI_ERROR, (byte*)varbuf, strlen(varbuf) );
}

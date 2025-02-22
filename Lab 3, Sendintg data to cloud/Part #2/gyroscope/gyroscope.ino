#include <TensorFlowLite.h>
#include <Arduino.h>
#include "avr/dtostrf.h"
#include <Arduino_LSM9DS1.h>
#include "custom_serialcom.h"
#include "main_functions.h"
#include "model_accel.h"
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_log.h"
#include "tensorflow/lite/micro/system_setup.h"
#include "tensorflow/lite/schema/schema_generated.h"

#define RED_PIN    22
#define GREEN_PIN  23
#define BLUE_PIN   24
#define YELLOW_PIN LED_BUILTIN
#define NO_PIN     -1

// Globals
namespace {
  char varbuf[64];
  const float accelerationThreshold = 1.5; // in G's

  const tflite::Model* tflModel = nullptr;
  tflite::MicroInterpreter* tflInterpreter = nullptr;
  TfLiteTensor* tflInputTensor = nullptr;
  TfLiteTensor* tflOutputTensor = nullptr;
  static tflite::AllOpsResolver tflOpsResolver;

  const int kTensorArenaSize = 8000;
  uint8_t tensorArena[kTensorArenaSize];
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
  light_led(NO_PIN);

  tflite::InitializeTarget();
  tflModel = tflite::GetModel(g_model);
  if (tflModel->version() != TFLITE_SCHEMA_VERSION) {
    HandleOutput_error(-100);
    while (1);
  }
  
  static tflite::MicroInterpreter static_interpreter(
    tflModel, tflOpsResolver, tensorArena, kTensorArenaSize);
  tflInterpreter = &static_interpreter;
  
  TfLiteStatus allocate_status = tflInterpreter->AllocateTensors();
  if (allocate_status != kTfLiteOk) {
    HandleOutput_error(-101);
    while(1);
  }

  tflInputTensor = tflInterpreter->input(0);
  tflOutputTensor = tflInterpreter->output(0);
  HandleOutput_status(1);
}

void loop() {
  float aX, aY, aZ;
  float_t* input_buff = tflInputTensor->data.f;
  float_t* output_buff = tflOutputTensor->data.f;

  // wait for significant motion
  while(1) {
    light_led(NO_PIN);
    light_led(GREEN_PIN);
    
    while(1) {
      if (IMU.accelerationAvailable()) {
        IMU.readAcceleration(aX, aY, aZ);
        
        // Check for significant motion
        float aSum = fabs(aX) + fabs(aY) + fabs(aZ);
        if (aSum >= accelerationThreshold) break;
      }
    }
    light_led(NO_PIN);

    // Only use accelerometer values
    input_buff[0] = aX;
    input_buff[1] = aY;
    input_buff[2] = aZ;
    
    HandleOutput_double(aX);
    HandleOutput_double(aY);
    HandleOutput_double(aZ);

    // Run inference
    TfLiteStatus invoke_status = tflInterpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
      HandleOutput_error(-102);
      while(1);
    }

    HandleOutput_double(output_buff[0]);
    HandleOutput_double(output_buff[1]);

    if (output_buff[0] > output_buff[1]) light_led(BLUE_PIN);
    else light_led(YELLOW_PIN);

    delay(2000);
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

void light_led(int color) {
  if (color == NO_PIN) {
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, HIGH);
    digitalWrite(BLUE_PIN, HIGH);
    digitalWrite(YELLOW_PIN, LOW);
  }
  else {
    if (color == YELLOW_PIN) {
      digitalWrite(color, HIGH);
    }
    else {
      digitalWrite(color, LOW);
    }
  }
}
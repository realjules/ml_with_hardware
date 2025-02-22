// Create the .cpp file from a TensorFlow Lite flatbuffer like this:
// xxd -i model.tflite > model.cpp
//
// Edit the model.cpp file to start like this:
// #include "model.h"
// alignas(8) const unsigned char g_model[] = {
//
// it should end like this (of course leave = and the number unchanged!):
// const int g_model_len

// This is a standard TensorFlow Lite model file that has been converted into a
// C data array, so it can be easily compiled into a binary for devices that
// don't have a file system.

#ifndef TFLM_PERK_MODEL_H_
#define TFLM_PERK_MODEL_H_

extern const unsigned char g_model[];
extern const int g_model_len;

#endif

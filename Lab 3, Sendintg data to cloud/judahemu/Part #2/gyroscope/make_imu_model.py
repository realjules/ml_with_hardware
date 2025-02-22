#!/usr/bin/python3
import os
import sys
import math
import numpy as np

import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

MODEL_TF = 'model_accel.keras'
MODEL_TFLITE = 'model_accel.tflite'
NUM_EPOCHS = 100
BATCH_SIZE = 50

seed = 123
tf.keras.utils.set_random_seed(seed)

# Read the training set and parse it - only use accelerometer columns
print("Loading data...")
dataFile = "imu_training_data.csv"
df = pd.read_csv(dataFile)

# Display dataset information
print("\nUnique labels in dataset:")
print(df.iloc[:,3].unique())
print("\nLabel counts:")
print(df.iloc[:,3].value_counts())

# Only select accelerometer columns (first 3) instead of all 6 columns
X = df.iloc[:,0:3].values  # Only ax, ay, az
y = df.iloc[:,3].values    # Labels remain the same

# Convert labels to numeric values
encoder = LabelEncoder()
y1 = encoder.fit_transform(y)
Y = pd.get_dummies(y1).values

num_classes = Y.shape[1]
print(f"\nNumber of classes: {num_classes}")

# Define model with correct number of output classes
model = tf.keras.Sequential([
    tf.keras.layers.Dense(10, activation='relu', input_shape=(3,)),
    tf.keras.layers.Dense(10, activation='relu'),
    tf.keras.layers.Dense(num_classes, activation='softmax')  # Dynamic number of classes
])

model.compile(optimizer='rmsprop',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Split data and train
X_train, X_test, y_train, y_test = train_test_split(X, Y, 
                                    test_size=0.2, random_state=seed)

print("\nTraining model...")
history = model.fit(X_train, y_train, 
                   batch_size=BATCH_SIZE, 
                   epochs=NUM_EPOCHS,
                   validation_split=0.2,
                   verbose=1)

# Evaluate model
print("\nEvaluating model...")
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print('Test loss:', loss)
print('Test accuracy:', accuracy)

# Compare predictions
actual = np.argmax(y_test, axis=1)
y_pred = model.predict(X_test)
predicted = np.argmax(y_pred, axis=1)
print("\nSample predictions:")
print(f"Actual:    {actual[:10]}")
print(f"Predicted: {predicted[:10]}")

# Save full model
print("\nSaving Keras model...")
model.save(MODEL_TF)

# Convert to TFLite
print("\nConverting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
open(MODEL_TFLITE, 'wb').write(tflite_model)
basic_model_size = os.path.getsize(MODEL_TFLITE)
print(f"TFLite model size: {basic_model_size} bytes")

# Verify TFLite model
print("\nVerifying TFLite model...")
interpreter = tf.lite.Interpreter(MODEL_TFLITE)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Test TFLite model predictions
x_test_ = X_test.astype(np.float32)
output_shape = output_details[0]['shape']
y_pred_tflite = np.empty([len(x_test_), output_shape[1]], 
                        dtype=output_details[0]["dtype"])

for i in range(len(x_test_)):
    interpreter.set_tensor(input_details[0]["index"], [x_test_[i]])
    interpreter.invoke()
    y_pred_tflite[i] = interpreter.get_tensor(output_details[0]["index"])[0]

tflite_predicted = np.argmax(y_pred_tflite, axis=1)
print("\nAccuracy Comparison:")
print(f"Sample of 10 predictions:")
print(f"Actual:           {actual[:10]}")
print(f"Keras Predicted:  {predicted[:10]}")
print(f"TFLite Predicted: {tflite_predicted[:10]}")

# Calculate overall accuracy
keras_accuracy = np.mean(predicted == actual)
tflite_accuracy = np.mean(tflite_predicted == actual)
print(f"\nFinal Accuracy:")
print(f"Keras Model:  {keras_accuracy:.4f}")
print(f"TFLite Model: {tflite_accuracy:.4f}")
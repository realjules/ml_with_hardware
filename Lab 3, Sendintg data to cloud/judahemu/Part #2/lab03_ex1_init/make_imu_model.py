#!/users/robot/AppData/Local/Programs/Python/Python310
import os
import sys
import math
import numpy as np

import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

MODEL_TF = 'model.keras'
MODEL_TFLITE = 'model.tflite'
NUM_EPOCHS = 100
BATCH_SIZE = 50

seed = 123
tf.keras.utils.set_random_seed(seed)

# Define a model and compile it
model = tf.keras.Sequential([ \
                   tf.keras.layers.Dense(10, activation='relu'), \
                   tf.keras.layers.Dense(10, activation='relu'), \
                   tf.keras.layers.Dense(2, activation='softmax')
                            ])

model.compile(optimizer='rmsprop', \
              loss='categorical_crossentropy', \
              metrics=['accuracy'])

# Read the training set and parse it
dataFile = "imu_training_data.csv"
df = pd.read_csv(dataFile)
X = df.iloc[:,0:6].values
y = df.iloc[:,6].values

# Convert the y values, which are currently in text,
# into numeric values.  A different value for each class
encoder = LabelEncoder()
y1 = encoder.fit_transform(y)
#print(f"labels are {y1}")

# Create a one-shot vector for the outputs.  As this
# data set has 2 classes, it is a sequence of vectors, each of length 2.
# A "1" in the appropriate location indicates class membership
Y = pd.get_dummies(y1).values
#print(f"Y =  {Y}")

# Split the data set and train the model
X_train, X_test, y_train, y_test = train_test_split(X, Y, \
                                        test_size=0.2,random_state=seed)
model.fit(X_train, y_train, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS)

# Use the test set to evaluate the model.  Then look 
# at the predictions
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print('Test loss: ', loss)
print('Test accuracy: ', accuracy)

actual = np.argmax(y_test, axis=1)
y_pred = model.predict(X_test)
predicted =  np.argmax(y_pred,axis=1)
print(f"Actual:    {actual}")
print(f"Predicted: {predicted}")

# Save the full model to disk
model.save(MODEL_TF)

#----------
# Create a tensorflow lite model, save it to disk,
# and check its size. Then read it back in (to prove we can).
# Then do some predictions with the tflite model.
# Note that here we are creating an interpreter in python
# that should give the same results as when we execute on the Arduino
#----------

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
open(MODEL_TFLITE, 'wb').write(tflite_model)
basic_model_size = os.path.getsize(MODEL_TFLITE)
print(f"tflite model size is {basic_model_size} bytes")
tfl_interpreter = tf.lite.Interpreter(MODEL_TFLITE)

tfl_interpreter.allocate_tensors()
input_details = tfl_interpreter.get_input_details()
output_details = tfl_interpreter.get_output_details()

print(f"\ninput_details = {input_details}\n")
print(f"output_details = {output_details}\n")

x_test_ = X_test.copy()
x_test_ = x_test_.astype(np.float32)
print(f"x_test_.shape = {x_test_.shape}")
print(f"len(x_test_) = {len(x_test_)}")
print(f"x_test_.size = {x_test_.size}\n")

output_shape = output_details[0]['shape']
y_pred_tflite = np.empty([ len(x_test_), output_shape[1] ], \
                              dtype=output_details[0]["dtype"])
for i in range(len(x_test_)):
  tfl_interpreter.set_tensor(input_details[0]["index"], [x_test_[i]])
  tfl_interpreter.invoke()
  y_pred_tflite[i] = \
            tfl_interpreter.get_tensor(output_details[0]["index"])[0]
  print(f"y_pred_tflite[{i}] = {y_pred_tflite[i]}")

print(f"\ny_pred - y_pred_tflite\n = {y_pred - y_pred_tflite}")

tflite_predicted =  np.argmax(y_pred_tflite,axis=1)
print(f"Actual:             {actual}")
print(f"Predicted:          {predicted}")
print(f"Tflite Predicted:   {tflite_predicted}")
print(f"Actual - Predicted: {np.abs(actual - predicted)}")
print(f"pred - tflitepred:  {np.abs(predicted - tflite_predicted)}")

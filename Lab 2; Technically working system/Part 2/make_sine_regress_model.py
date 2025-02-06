#!/home/robot/perkvenv/bin/python3
import os
import sys
import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
import math

# -------------------------------
# Train a model
# -------------------------------
OUT_PLOTS_DIR = './plots/'
MODEL_TF = 'model.tf'
MODEL_TFLITE = 'model.tflite'

# Set parameters for model training
seed = 123
tf.keras.utils.set_random_seed(seed)
NUM_EPOCHS = 400
SAMPLES = 5000

# Generate noisy sinusoidal data
x_values = np.random.uniform(0, 2 * math.pi, size=SAMPLES).astype(np.float32)
np.random.shuffle(x_values)
y_values = np.sin(x_values).astype(np.float32) + 0.1 * np.random.randn(*x_values.shape)

plt.plot(x_values, y_values, 'b.', label="Raw Samples")
plt.legend()
plt.xticks()
plt.yticks()
plt.grid(True)
plt.savefig(OUT_PLOTS_DIR + 'plot0.png')
plt.close()

# Splitting data
TRAIN_SPLIT = int(0.6 * SAMPLES)
TEST_SPLIT = int(0.2 * SAMPLES + TRAIN_SPLIT)
x_train, x_test, x_validate = np.split(x_values, [TRAIN_SPLIT, TEST_SPLIT])
y_train, y_test, y_validate = np.split(y_values, [TRAIN_SPLIT, TEST_SPLIT])

plt.plot(x_train, y_train, 'b.', label="Train")
plt.plot(x_test, y_test, 'r.', label="Test")
plt.plot(x_validate, y_validate, 'y.', label="Validate")
plt.legend()
plt.xticks()
plt.yticks()
plt.grid(True)
plt.savefig(OUT_PLOTS_DIR + 'plot1.png')
plt.close()

# Define the neural network model
# Updated with larger layers and an additional layer
model = tf.keras.Sequential([
    keras.layers.Dense(32, activation='relu', input_shape=(1,)),  # Increased from 16 to 32
    keras.layers.Dense(32, activation='relu'),  # Increased from 16 to 32
    keras.layers.Dense(32, activation='relu'),  # New layer added
    keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss="mse", metrics=["mae"])
history = model.fit(x_train, y_train, epochs=NUM_EPOCHS, batch_size=64, validation_data=(x_validate, y_validate))
model.save(MODEL_TF)

# Visualizing training performance
SKIP = 10
epochs = range(SKIP, len(history.history['loss']))

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(epochs, history.history['loss'][SKIP:], 'g.', label='Training Loss')
plt.plot(epochs, history.history['val_loss'][SKIP:], 'b.', label='Validation Loss')
plt.title('Loss Over Training')
plt.xlabel('Epochs')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(epochs, history.history['mae'][SKIP:], 'g.', label='Training MAE')
plt.plot(epochs, history.history['val_mae'][SKIP:], 'b.', label='Validation MAE')
plt.title('Mean Absolute Error Over Training')
plt.xlabel('Epochs')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig(OUT_PLOTS_DIR + 'plot2.png')
plt.close()

# Evaluate the model
test_loss, test_mae = model.evaluate(x_test, y_test)
y_test_pred = model.predict(x_test)
mse_tf = np.mean((y_test - y_test_pred.flatten())**2)

print(f"\nTF Model Performance: Loss={test_loss:.6f}, MAE={test_mae:.6f}, MSE={mse_tf:.6f}")

# --------------------------------------------------------
# Convert model to TensorFlow Lite with quantization
# --------------------------------------------------------
converter = tf.lite.TFLiteConverter.from_saved_model(MODEL_TF)

# Updated quantization configuration
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # Changed from EXPERIMENTAL_SPARSITY

# Define representative dataset generator for quantization
def representative_data_gen():
    for i in range(300):
        yield [tf.dtypes.cast(x_train[i:i+1], tf.float32)]

converter.representative_dataset = representative_data_gen
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.float32
converter.inference_output_type = tf.float32

tflite_model = converter.convert()

# Save the tflite model to disk and compare sizes
open(MODEL_TFLITE, 'wb').write(tflite_model)
quant_model_size = os.path.getsize(MODEL_TFLITE)

# Calculate and display size reduction
size_reduction = (1 - quant_model_size / os.path.getsize(MODEL_TF)) * 100
print(f"\nTF Lite Model Size: {quant_model_size} bytes ({size_reduction:.2f}% reduction)")

# Run inference on the quantized model
x_test_reshaped = x_test.copy().reshape((x_test.size, 1)).astype(np.float32)
tfl_interpreter = tf.lite.Interpreter(MODEL_TFLITE)
tfl_interpreter.allocate_tensors()
input_details = tfl_interpreter.get_input_details()
output_details = tfl_interpreter.get_output_details()

print(f"Input Details: {input_details}")
print(f"Output Details: {output_details}")

y_test_pred_tflite = np.empty(x_test.size, dtype=output_details[0]["dtype"])

for i in range(len(x_test)):
    tfl_interpreter.set_tensor(input_details[0]["index"], [x_test[i]])
    if i % 50 == 0:  # Added conditional check for periodic invocation
        tfl_interpreter.invoke()
    y_test_pred_tflite[i] = tfl_interpreter.get_tensor(output_details[0]["index"])[0]

# Calculate MSE for TFLite model
mse_tflite = np.mean((y_test - y_test_pred_tflite)**2)
print(f"TF Lite Model: MSE={mse_tflite:.6f}")

# Compare model predictions
plt.clf()
plt.title('Comparison: TF vs. TF Lite Model Predictions')
plt.plot(x_test, y_test, 'r.', label='Actual Values')
plt.plot(x_test, y_test_pred, 'g.', label='TF Predictions')
plt.plot(x_test, y_test_pred_tflite, 'm.', label='Quantized TFLite Predictions')
plt.legend()
plt.grid(True)
plt.savefig(OUT_PLOTS_DIR + 'plot4.png')
plt.close()
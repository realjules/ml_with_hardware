#!/home/robot/perkvenv/bin/python3

"""
TensorFlow Lite Model Validation Script
This script communicates with an Arduino running a TFLite model,
captures predicted values, and compares them with ideal values.
"""

import numpy as np
import sys
import csc_io as csc
import matplotlib.pyplot as plt

# Constants
MAX_SAMPLES = 500
DATA_OUTPUT_PATH = 'logs_quantitazed.txt'
PLOT_OUTPUT_PATH = "plot_quantitazed.png"
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

def main():
    # Validate command line arguments
    if len(sys.argv) != 1:
        print("Usage: rpicom")
        sys.exit(1)

    # Initialize serial communication
    csc.rpi_init(SERIAL_PORT, BAUD_RATE)

    # Initialize data collection
    sample_count = 0
    predicted_x = []
    predicted_y = []

    # Collect data from Arduino
    while sample_count < MAX_SAMPLES:
        # Signal Arduino ready for next command
        csc.rpi_tell_ard_ready()
        
        # Process Arduino commands
        arduino_command = csc.rpi_get_ard_cmd()
        
        if arduino_command == csc.CMD_READ_PI:
            # Handle Arduino read request
            input()  # Wait for user input
            
        elif arduino_command == csc.CMD_WRITE_PI_ERROR:
            # Handle error messages from Arduino
            error_message = csc.rpi_get_data().decode('utf-8')
            print(f"*** ERROR ***: {error_message}")
            
        elif arduino_command == csc.CMD_WRITE_PI_MLX:
            # Receive and store X coordinate
            x_coordinate = float(csc.rpi_get_data().decode('utf-8'))
            print(f"X coordinate: {x_coordinate}")
            predicted_x.append(x_coordinate)
            
        elif arduino_command == csc.CMD_WRITE_PI_MLY:
            # Receive and store Y coordinate
            y_coordinate = float(csc.rpi_get_data().decode('utf-8'))
            print(f"Y coordinate: {y_coordinate}")
            predicted_y.append(y_coordinate)
            sample_count += 1
            
        else:
            print("ERROR: Unexpected command received")
            sys.exit(1)

    # Save collected data to file
    save_data_to_file(predicted_x, predicted_y, DATA_OUTPUT_PATH)
    
    # Generate and save comparison plot
    generate_comparison_plot(predicted_x, predicted_y, PLOT_OUTPUT_PATH)

def save_data_to_file(x_values, y_values, filepath):
    """Save collected X,Y coordinates to file"""
    with open(filepath, "w") as output_file:
        for x, y in zip(x_values, y_values):
            output_file.write(f'{x} {y}\n')
    print(f"Data saved to {filepath}")

def generate_comparison_plot(x_values, y_values, plot_path):
    """Generate and save plot comparing predicted vs ideal values"""
    # Convert to numpy arrays for calculations
    x_array = np.array(x_values)
    
    # Calculate ideal half-wave rectified sine values
    ideal_values = np.maximum(0, np.sin(x_array)).astype(np.float32)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(x_array, y_values, 'b-', label='predicted values', marker='o')
    plt.plot(x_array, ideal_values, 'r-', label='ideal values', marker='o')
    
    # Add plot details
    plt.xlabel('x values')
    plt.ylabel('y values')
    plt.title('MLX and MLY predicted and ideal values')
    plt.legend()
    
    # Save plot
    plt.savefig(plot_path)
    print(f"Plot saved as {plot_path}")

if __name__ == "__main__":
    main()
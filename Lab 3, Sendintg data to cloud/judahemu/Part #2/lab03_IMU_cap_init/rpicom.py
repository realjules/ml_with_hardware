#!/home/robot/perkvenv/bin/python3
import time
import sys
import csc_io as csc
import os.path
import os

class IMUDataCollector:
    def __init__(self):
        self.current_values = []
        self.is_first_value = True
        self.sample_count = 0
        self.SAMPLES_PER_SET = 20

    def init_csv_file(self, filename="imu_training_data.csv"):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write("ax, ay, az, gx, gy, gz, movement_type\n")

    def format_number(self, value):
        """Format number to match required format with proper spacing and leading zeros"""
        if abs(value) < 1:
            if value >= 0:
                return f" 0{value:.3f}"
            else:
                return f"-0{abs(value):.3f}"
        return f" {value:.3f}"

    def process_value(self, data_bytes, movement_type, filename="imu_training_data.csv"):
        """Process each incoming IMU value"""
        value = float(data_bytes.decode().strip())
        
        # Skip the first demo value
        if self.is_first_value:
            self.is_first_value = False
            return
                
        # Add value to current collection
        self.current_values.append(value)
        
        # If we have 6 values, write them to CSV
        if len(self.current_values) == 6:
            # Format values with consistent spacing
            formatted_values = [self.format_number(val) for val in self.current_values]
            line = ",".join(formatted_values) + f",{movement_type}\n"
            
            # Write to file
            with open(filename, 'a') as f:
                f.write(line)
            
            # Reset for next set
            self.current_values = []
            self.sample_count += 1
            print(f"\nSaved sample {self.sample_count}")

            # Check if we've completed a set of 20
            if self.sample_count % self.SAMPLES_PER_SET == 0:
                while True:
                    print("\nCompleted 20 samples. Choose next action:")
                    print("1. Collect 'drop' movements")
                    print("2. Collect 'side' movements")
                    print("3. Exit")
                    choice = input("Enter your choice (1/2/3): ").strip()
                    
                    if choice == '1':
                        return 'drop'
                    elif choice == '2':
                        return 'side'
                    elif choice == '3':
                        print(f"\nCollection complete! Total samples: {self.sample_count}")
                        sys.exit(0)
                    else:
                        print("Invalid input. Please enter 1, 2, or 3")

def get_initial_movement_type():
    while True:
        print("\nChoose movement type to collect:")
        print("1. Collect 'drop' movements")
        print("2. Collect 'side' movements")
        choice = input("Enter your choice (1/2): ").strip()
        
        if choice == '1':
            return 'drop'
        elif choice == '2':
            return 'side'
        else:
            print("Invalid input. Please enter 1 or 2")

if len(sys.argv) != 1:
    print("usage is: rpicom")
    sys.exit(1)

collector = IMUDataCollector()
collector.init_csv_file()  # Initialize CSV with headers
csc.rpi_init('/dev/ttyACM0', 115200)

# Get initial movement type
movement_type = get_initial_movement_type()

print(f"\nStarting collection of {movement_type} movement data...")
print("Move the device when the GREEN LED is on")
print(f"Will collect sets of 20 samples of {movement_type} movements\n")

while(True):
    # Tell the Arduino we are ready to process a command
    csc.rpi_tell_ard_ready()

    # Read the command and process it
    ard_cmd = csc.rpi_get_ard_cmd()
    if ard_cmd == csc.CMD_READ_PI:
        print("\nEnter a floating point number (e.g., 1):")
        float2send = input()
        csc.rpi_send_string(str(float2send))
    elif ard_cmd == csc.CMD_WRITE_PI_ERROR:
        print(f"\n*** ERROR ***: {csc.rpi_get_data()}")
    elif ard_cmd == csc.CMD_WRITE_PI_LOG:
        data = csc.rpi_get_data()
        new_movement_type = collector.process_value(data, movement_type)
        if new_movement_type:  # If user selected a new movement type
            movement_type = new_movement_type
            print(f"\nSwitching to {movement_type} movement collection...")
            print("Move the device when the GREEN LED is on")
    elif ard_cmd == csc.CMD_WRITE_PI_STATUS:
        status = csc.rpi_get_data()
        current_sample = int(status.decode().strip())
        print(f"\nCapturing sample {current_sample} in current set...")
    else:
        print("\nERROR: this shouldn't happen")
        sys.exit(1)
    if(os.path.exists("STOPME")):
        os.remove("STOPME")
        sys.exit(1)

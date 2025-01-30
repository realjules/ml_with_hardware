import time
import sys
import csc_io as csc
import os.path
import os

# Constants
MAX_VALUES = 500
LOG_FILENAME = "logs/log_values.txt"

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Initialize counter for captured values
captured_values = 0

if len( sys.argv ) != 1 :
    print("usage is: rpicom")
    sys.exit(1)

csc.rpi_init('/dev/ttyACM0', 115200)

# Open log file
log_file = open(LOG_FILENAME, 'w')

while(True):
    # Tell the Arduino we are ready to process a command
    csc.rpi_tell_ard_ready()
    
    # Read the command and process it
    ard_cmd = csc.rpi_get_ard_cmd()
    
    if ard_cmd == csc.CMD_READ_PI:
        # Arduino wants to read from RPi
        print("Press CR to continue...")
        input() # Reads the CR
        csc.rpi_send_string("3.1416") #sends the string
        
    elif ard_cmd == csc.CMD_WRITE_PI_ERROR:
        # Arduino is sending RPi an error message
        print(f"*** ERROR ***: {csc.rpi_get_data()}")
        
    elif ard_cmd == csc.CMD_WRITE_PI_LOG:
        # Arduino is sending RPi a log message
        log_data = csc.rpi_get_data()
        print(f"LOG: {log_data}")
        
        # Write to log file if we haven't captured enough values
        if captured_values < MAX_VALUES:
            log_file.write(f"{log_data}\n")
            log_file.flush()  # Ensure data is written immediately
            captured_values += 1
            
            # Close file and exit when we have enough values
            if captured_values >= MAX_VALUES:
                print(f"Captured {MAX_VALUES} values. Output saved to {LOG_FILENAME}")
                log_file.close()
                sys.exit(0)
                
    elif ard_cmd == csc.CMD_WRITE_PI_STATUS:
        # Arduino is sending RPi a log message
        print(f"STATUS: {csc.rpi_get_data()}")
        
    else:
        print("ERROR: this shouldn't happen")
        log_file.close()
        sys.exit(1)
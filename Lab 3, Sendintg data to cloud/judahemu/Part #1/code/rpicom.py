#!/home/robot/perkvenv/bin/python3
import numpy as np
import sys
import csc_io as csc
import matplotlib.pyplot as plt
from datetime import datetime
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "XXXXXXX"  # Replace with your email
RECEIVER_EMAIL = "XXXXXXX"  # Replace with recipient email
APP_PASSWORD = "XXXXXXX"  # Replace with your app password

# Initialize communication
if len(sys.argv) != 1:
    print("usage is: rpicom")
    sys.exit(1)

csc.rpi_init('/dev/ttyACM0', 9600)  # Changed baud rate to match Arduino sketch

# Lists to store temperature values and timestamps
temp_values = []
timestamps = []
last_email_time = None

def send_email_with_graph(image_path, temp_data):
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL
    message["Subject"] = "Hourly Temperature Report"
    
    body = f"Temperature Report\n"
    body += f"Number of readings: {len(temp_data)}\n"
    body += f"Latest temperature: {temp_data[-1]:.2f}°C\n"
    body += f"Average temperature: {sum(temp_data)/len(temp_data):.2f}°C"
    message.attach(MIMEText(body, "plain"))
    
    with open(image_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={image_path}"
    )
    message.attach(part)
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(message)

def create_temp_plot():
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, temp_values, 'b-', label='Temperature')
    plt.title('Temperature Over Time')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    
    # Save the plot
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'temperature_plot_{timestamp}.png'
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    return filename

try:
    while True:
        # Tell the Arduino we are ready to process a command
        csc.rpi_tell_ard_ready()
        
        # Read the command and process it
        ard_cmd = csc.rpi_get_ard_cmd()
        
        if ard_cmd == csc.CMD_WRITE_PI_LOG:
            # Arduino is sending a temperature reading
            log_entry = csc.rpi_get_data().decode('utf-8')
            
            if log_entry.startswith("TEMP:"):
                # Extract temperature value
                temp = float(log_entry.split(":")[1])
                current_time = datetime.now()
                
                # Store the data
                temp_values.append(temp)
                timestamps.append(current_time)
                
                print(f"Temperature recorded: {temp:.2f}°C at {current_time}")
                
                # Check if it's time to send an email (hourly)
                if last_email_time is None or (current_time - last_email_time).total_seconds() >= 3600:
                    if len(temp_values) > 0:
                        plot_file = create_temp_plot()
                        send_email_with_graph(plot_file, temp_values)
                        last_email_time = current_time
                        print(f"Email sent with temperature plot at {current_time}")
        
        elif ard_cmd == csc.CMD_WRITE_PI_ERROR:
            # Arduino is sending an error message
            error_message = csc.rpi_get_data().decode('utf-8')
            print(f"*** ERROR ***: {error_message}")
        
        else:
            print(f"Unexpected command: {ard_cmd}")

except KeyboardInterrupt:
    print("\nMonitoring stopped by user")
    # Create final plot before exiting
    if len(temp_values) > 0:
        final_plot = create_temp_plot()
        print(f"Final plot saved as {final_plot}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Clean up
    print("Exiting...")

#!/usr/bin/python3
import time
import sys
import csc_io as csc
import os.path
import os

if len( sys.argv ) != 1 :
  print("usage is: rpicom")
  sys.exit(1)

csc.rpi_init('/dev/ttyACM0', 115200)
while(True):
  # Tell the Arduino we are ready to process a command
  csc.rpi_tell_ard_ready()

  # Read the command and process it
  ard_cmd = csc.rpi_get_ard_cmd()
  if ard_cmd == csc.CMD_READ_PI:
    # Arduino wants to read from RPi
    #print("Press CR to continue...")
    #input()
    csc.rpi_send_string( "3.14" )
  elif ard_cmd == csc.CMD_WRITE_PI_ERROR:
    # Arduino is sending RPi an error message
    print(f"*** ERROR ***: {csc.rpi_get_data()}")
  elif ard_cmd == csc.CMD_WRITE_PI_LOG:
    # Arduino is sending RPi a log message
    print(f"LOG: {csc.rpi_get_data()}")
  elif ard_cmd == csc.CMD_WRITE_PI_STATUS:
    # Arduino is sending RPi a log message
    print(f"STATUS: {csc.rpi_get_data()}")
  elif ard_cmd == csc.CMD_WRITE_PI_AX:
    ax = csc.rpi_get_data()
    ax = ax.decode('utf-8')
  elif ard_cmd == csc.CMD_WRITE_PI_AY:
    ay = csc.rpi_get_data()
    ay = ay.decode('utf-8')
  elif ard_cmd == csc.CMD_WRITE_PI_AZ:
    az = csc.rpi_get_data()
    az = az.decode('utf-8')
  elif ard_cmd == csc.CMD_WRITE_PI_GX:
    gx = csc.rpi_get_data()
    gx = gx.decode('utf-8')
  elif ard_cmd == csc.CMD_WRITE_PI_GY:
    gy = csc.rpi_get_data()
    gy = gy.decode('utf-8')
  elif ard_cmd == csc.CMD_WRITE_PI_GZ:
    gz = csc.rpi_get_data()
    gz = gz.decode('utf-8')
    print(f"{ax}  {ay}  {az}  {gx}  {gy}  {gz}")
  else:
    print("ERROR: this shouldn't happen")
    sys.exit(1)
  if( os.path.exists("STOPME") ):
    os.remove("STOPME");
    sys.exit(1)

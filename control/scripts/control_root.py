# WARNING: This script is intended to run with root privileges!
# SANITIZE ALL INPUTS AND DO NOT ALLOW UNAUTHORIZED MODIFICATION!

# Purpose: Helper script to control GPIO pins as root.
# Intended to be run from a webserver that's not running with root privileges.

# Arguments: control_root.py <read/write> <pin (board numbering)> [value if write]

from RPi import GPIO
import sys
import os

if os.geteuid() != 0:
    print("Not running as root! Terminating!\n")
    sys.exit(1)

if len(sys.argv) < 3:
    print("Not enough arguments!\n")
    print("Usage: control_root.py <read/write> <pin (board numbering)> [value if write]\n")
    sys.exit(1)

# Get rid of the print warnings warning us that the pins are already in use.
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

mode = sys.argv[1]
pin = int(sys.argv[2])
GPIO.setup(pin, GPIO.OUT)

if mode == 'read':
    # Read PIN and exit with the code
    sys.exit(GPIO.input(pin))
elif mode == 'write':
    # Write the value and exit with code 0
    val = int(sys.argv[3])
    GPIO.output(pin, val)
    sys.exit(0)
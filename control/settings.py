import os
from thermoctrl.settings import BASE_DIR
from control.models import ControlEvent, GlobalSetting

# Pin settings for various accessories
# Pins are numbered as pins on the BCM!
PIN_FANCTRL = 17 # white
PIN_COOLCTRL = 27 # blue
PIN_HEATCTRL = 22 # gray
PIN_MASTER = 23 # orange

def getGlobal(name, default):
    try:
        s = GlobalSetting.objects.get(key=name)
        return s.value
    except GlobalSetting.DoesNotExist as e:
        return default

def setGlobal(name, value):
    s = GlobalSetting(key=name, value=value)
    s.save()

def get_target_temp():
    return float(getGlobal('target_temp', '21.5')) # Return about 73 deg fahrenheit if key DNE

# Sets the target temperature (in celsius)
def set_target_temp(temp):
    setGlobal('target_temp', str(temp))

# Wait until we reach this high of a delta before turning on the controls (in deg celsius)
TEMP_ON_SWIVEL = .8
# Wait until we reach this high of a delta before turning off the controls
# AKA: How many degrees should we overshoot the target?
TEMP_OFF_SWIVEL = .1
# If the temperature doesn't lower by this amount in a certain amount of time, assume the
# unit is frozen and begin a defrost period.
TEMP_DEFROST_THRESHOLD = 0.01

# How many minutes to wait for the AC to defrost
COOL_DEFROST_TIME = 40
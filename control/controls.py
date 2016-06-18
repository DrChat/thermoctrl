from subprocess import call, Popen
from thermoctrl.settings import BASE_DIR, PRODUCTION_SERVER
from django.utils import timezone
import os
import sys

from control import settings
from models import ControlEvent
import pigpio
pi = pigpio.pi()

def controlPin(pin, state, spec_data=None):
    """
    Controls a pin and creates a control event
    """

    evt = ControlEvent()
    evt.time = timezone.now()
    type = None

    if pin == settings.PIN_FANCTRL:
        type = ControlEvent.EVENT_TYPE_FAN
    elif pin == settings.PIN_COOLCTRL:
        type = ControlEvent.EVENT_TYPE_COOL
    elif pin == settings.PIN_HEATCTRL:
        type = ControlEvent.EVENT_TYPE_HEAT
    else:
        # Uhoh!
        raise RuntimeError('Invalid pin passed to controlPin!')

    evt.type = type
    evt.val = state
    evt.spec_data = spec_data

    setPin(pin, state)
    evt.save()

def controlOverride(enabled):
    evt = ControlEvent()
    evt.time = timezone.now()
    evt.type = ControlEvent.EVENT_TYPE_OVERRIDE
    evt.val = enabled
    evt.save()
    
    settings.setGlobal('override_auto', enabled)

# N.B: We're flipping the state because of our hardware setup. Pins set to low
# turn on our relay, while setting pins to high turns it off.
def setPin(pin, state):
    if PRODUCTION_SERVER:
        return pi.write(pin, state == 0)

def readPin(pin):
    if PRODUCTION_SERVER:
        return pi.read(pin) == 0
    else:
        return 0
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from control import settings, controls
from control.models import ControlEvent
from common import tempsensor
from templog.models import Temp

def get_current_temp():
    ids = tempsensor.getSensorIDs()
    if len(ids) <= 0:
        logPrint("Uhoh! No sensor detected!")
        return 0
    elif len(ids) > 1:
        logPrint("More than one sensor detected! Using first one!")

    # Just default to the first one detected
    sensor = tempsensor.getSensor(ids[0])
    readTemp = sensor.read_temp()

    return readTemp[0]

def logPrint(msg):
    time = datetime.now()

    print(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg)

class Command(BaseCommand):
    help = 'Runs the AC control logic. Best to run this from a cron job.'

    def handle(self, *args, **options):
        target_temp = settings.get_target_temp()
        current_temp = get_current_temp()

        # Stop here if the override is enabled.
        logPrint("Check override")
        if settings.getGlobal('override_auto', '0') == '1':
            logPrint("--ABORT-- Override is ON!")
            return

        # TODO: We need a way to check how long AC has been cooling, heating, etc.
        # SQL table with rows describing control events, such as cooling started, stopped, etc

        # Read recent control events from the past few hours to see what's happening
        threshold = timezone.now() - timedelta(hours=3)
        results = ControlEvent.objects.filter(time__gte=threshold)

        # Huh. No results. Set the AC appropriately and add a control event
        # Also run this if the last one was an override off
        if results.count() == 0 or (results.latest('time').type == ControlEvent.EVENT_TYPE_OVERRIDE and results.latest('time').val == 0):
            logPrint("No recent control events (or last one was override off)!")

            # Turn off the pins without adding a control event
            controls.setPin(settings.PIN_COOLCTRL, 0)
            controls.setPin(settings.PIN_HEATCTRL, 0)

            delta = abs(current_temp - target_temp)
            logPrint("Delta: %.2f (cur %.2f targ %.2f)" % (delta, current_temp, target_temp))
            if delta > settings.TEMP_ON_SWIVEL:
                # Turning these on implies the fan will be turned on too
                if current_temp < target_temp:
                    # Heating on

                    logPrint("Turning on heater and fan! (curtemp %.2f target %.2f)" % (current_temp, target_temp))

                    # Fan
                    if controls.readPin(settings.PIN_FANCTRL) == 0:
                        controls.controlPin(settings.PIN_FANCTRL, 1)
                    
                    controls.controlPin(settings.PIN_HEATCTRL, 1)
                elif current_temp > target_temp:
                    # Cooling on

                    logPrint("Turning on cooling and fan! (curtemp %.2f target %.2f)" % (current_temp, target_temp))

                    # First turn on the fan
                    if controls.readPin(settings.PIN_FANCTRL) == 0:
                        controls.controlPin(settings.PIN_FANCTRL, 1)
                    # Now let's get down! (as in the temperature is going down, not we're gonna party)
                    # Now we just need a cool pun... oh wait
                    controls.controlPin(settings.PIN_COOLCTRL, 1)
            elif delta < settings.TEMP_OFF_SWIVEL:
                # TODO: Turn off whatever's on
                pass

            return

        # Okay. Check the old results to see what's happening.
        # Ignore anything that isn't a cooling or heating event.
        events = results.filter(Q(type='C') | Q(type='H'))
        evt = events.latest('time')
        temp_delta = abs(current_temp - target_temp)

        if evt.type == ControlEvent.EVENT_TYPE_COOL and evt.val == 1:
            logPrint("AC last turned on. Checking to see if it needs to be turned off. (temp_delta %.2f)" % temp_delta)

            # Check if we need to turn the AC off, either because we think it's frozen over or because we've reached the target.
            evt_delta = timezone.now() - evt.time
            logPrint("AC turned on %d minutes ago" % (evt_delta.total_seconds() / 60))

            if current_temp < (target_temp - settings.TEMP_OFF_SWIVEL):
                logPrint("Turning AC off due to reached target temp - swivel")
                # Turn it off.
                controls.controlPin(settings.PIN_COOLCTRL, 0)
            elif evt_delta.total_seconds() > 30 * 60:
                logPrint("Checking if AC is frozen.")

                # 30 minutes, check to see if it's cooling.
                # Look back at the temperature logs for the past 15 min and compare that with the current temp
                # If it hasn't dropped below a certain threshold, assume the unit is frozen over and defrost
                # Also make sure there's enough of a delta between now and the last log so we don't compare
                # across a few seconds!
                # TODO: Select one that's close but not closer than 15 minutes so this check will run
                # FIXME: This check needs to be disabled if we just came out of an override and the last temp was taken
                # before the override.
                objs = Temp.objects.filter(time__gt=timezone.now()-timedelta(minutes=25))
                loggedTemp = objs[0]

                delta = timezone.now() - loggedTemp.time
                logPrint("Checking temperature taken %d minutes ago" % (delta.total_seconds() / 60))

                if (timezone.now() - loggedTemp.time).total_seconds() > 5 * 60:
                    logPrint("Temperature delta %.2f" % (current_temp - loggedTemp.temp))
                    if current_temp - loggedTemp.temp >= -0.01:
                        # Temperature hasn't lowered more than .01 deg celsius since cooling has started. We're not cooling!
                        logPrint("Temperature not falling enough since cooling has started, assuming AC is frozen.")
                        controls.controlPin(settings.PIN_COOLCTRL, 0, 'frozen')
                else:
                    logPrint("Abort frozen check, last logged temperature is too close to now!")
            else:
                logPrint("Leaving AC on.")
        elif evt.type == ControlEvent.EVENT_TYPE_HEAT and evt.val == 1:
            logPrint("Heater last turned on. Checking to see if it needs to be turned off. (temp_delta %.2f)" % temp_delta)

            if current_temp > (target_temp + settings.TEMP_OFF_SWIVEL):
                logPrint("Turning heater off due to reached target temp + swivel")
                # Turn it off.
                controls.controlPin(settings.PIN_HEATCTRL, 0)
            else:
                logPrint("Leaving heater on.")
        elif evt.val == 0:
            # AC/heater was turned off. Check to see if we need to turn it on.
            logPrint("AC last turned off. Checking to see if it needs to be turned on. (temp_delta %.2f)" % temp_delta)

            # Check to see if it was last frozen
            if evt.type == 'C' and evt.spec_data == 'frozen':
                logPrint("AC frozen, checking if we're past defrost period.")

                # Okay. Figure out if COOL_DEFROST_TIME minutes have passed since this event.
                delta = timezone.now() - evt.time
                if delta.total_seconds() / 60 < settings.COOL_DEFROST_TIME:
                    min_left = settings.COOL_DEFROST_TIME - (delta.total_seconds() / 60)

                    # :(, wait until after the defrost period ends
                    logPrint("Frozen, waiting until defrost period ends (%d minutes left)" % min_left)
                    return
                else:
                    logPrint("Continuing with logic, defrost period is over.")

            # TODO: We need to take a temperature snapshot here if we turn on the controls so later code
            # isn't confused when the current temp is higher than the latest snapshot (because the controls
            # were off) (for AC frozen check)
            if temp_delta > settings.TEMP_ON_SWIVEL:
                # Okay! Heat or cool?
                if current_temp < target_temp:
                    # Heating
                    logPrint("Turning on heater and fan! (curtemp %.2f target %.2f)" % (current_temp, target_temp))

                    # Fan
                    if controls.readPin(settings.PIN_FANCTRL) == 0:
                        controls.controlPin(settings.PIN_FANCTRL, 1)
                    
                    controls.controlPin(settings.PIN_HEATCTRL, 1)
                elif current_temp > target_temp:
                    # Cooling
                    logPrint("Turned on cooling and fan! (curtemp %.2f target %.2f)" % (current_temp, target_temp))

                    # First turn on the fan
                    if controls.readPin(settings.PIN_FANCTRL) == 0:
                        controls.controlPin(settings.PIN_FANCTRL, 1)

                    controls.controlPin(settings.PIN_COOLCTRL, 1)
            else:
                logPrint("Delta not big enough, exiting.")
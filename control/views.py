from django.contrib.auth import authenticate
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render, redirect
from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
from common.shortcuts import render_json, render_json_err
from common.sslredirect import get_secure_url

from control import controls, settings, models
from common import tempsensor, shortcuts

# TODO: With override, maybe have a timer option for how long the override should stay enabled.

def index(req):
    #if req.user.is_authenticated() and not req.is_secure():
    #    # Request not secure but user logged in. Change it.
    #    return HttpResponseRedirect(get_secure_url(req, True))

    params = {}

    params['override'] = int(settings.getGlobal('override_auto', 0))
    params['fan'] = controls.readPin(settings.PIN_FANCTRL)
    params['cool'] = controls.readPin(settings.PIN_COOLCTRL)
    params['heat'] = controls.readPin(settings.PIN_HEATCTRL)
    params['mobile'] = req.mobile
    params['authenticated'] = req.user.is_authenticated()
    params['user'] = req.user

    sensors = tempsensor.getSensorIDs()
    if len(sensors) > 0:
        sensor = tempsensor.getSensor(sensors[0])

        try:
            temp = sensor.read_temp()

            params['temp'] = 1
            params['temp_c'] = "%.2f" % temp[0]
            params['temp_f'] = "%.2f" % temp[1]
        except tempsensor.CouldNotReadError as e:
            params['temp'] = 0
            params['temp_err'] = "Could not read sensor file!"
    else:
        params['temp'] = 0
        params['temp_err'] = "No sensor detected!"

    return render(req, "control/index.html", params)

def switch(req):
    #if not req.user.is_authenticated():
    #    return render_json_err("You must be logged in to toggle the controls!");

    response = {}

    override = req.GET.get('override', None)
    fan = req.GET.get('fan', None)
    cool = req.GET.get('cool', None)
    heat = req.GET.get('heat', None)

    # Read in the current values
    coverride = settings.getGlobal('override_auto', '0') == '1'

    # Toggle? Figure out the new state.
    if override == 'toggle':
        override = coverride and 'off' or 'on'

    # Switch override on/off first
    if override == 'on' and not coverride:
        controls.controlOverride(1)
    elif override == 'off' and coverride:
        # Return because none of the logic will be enabled afterwards
        controls.controlOverride(0)
        return render_json({
            "status": "success",
            "override": "off",
        })
    
    if settings.getGlobal('override_auto', 0) == '0':
        return render_json_err("Automatic controls aren't overridden!")

    # Okay! Terminate now then.
    if not fan and not cool and not heat:
        return render_json({"override": override, "status": "success"})

    cfan = controls.readPin(settings.PIN_FANCTRL)
    ccool = controls.readPin(settings.PIN_COOLCTRL)
    cheat = controls.readPin(settings.PIN_HEATCTRL)
    if fan == 'toggle':
        fan = cfan and 'off' or 'on'
    if cool == 'toggle':
        cool = ccool and 'off' or 'on'
    if heat == 'toggle':
        heat = cheat and 'off' or 'on'

    # Can't have them both on at the same time!
    if (cool == 'on' and heat == 'on') or (ccool and heat == 'on') or (cheat and cool == 'on'):
        return render_json_err("Cannot turn heat and cool on at the same time!")

    # Don't allow the fan to be turned off if the cooler/heater is on.
    if fan == 'off' and ((cheat and heat != "off") or (ccool and cool != "off")):
        return render_json_err("Cannot turn off fan if cooler/heater is on!")

    # The fan needs to be turned on if cool/heat are turned on!
    if cool == 'on' or heat == 'on':
        fan = 'on'

    # Fan control
    if fan == 'on':
        controls.setPin(settings.PIN_FANCTRL, 1)
        #settings.setGlobal('override_fan', 1)
    elif fan == 'off':
        controls.setPin(settings.PIN_FANCTRL, 0)
        #settings.setGlobal('override_fan', 0)

    # Cool control
    if cool == 'on':
        controls.setPin(settings.PIN_COOLCTRL, 1)
        #settings.setGlobal('override_cool', 1)
    elif cool == 'off':
        controls.setPin(settings.PIN_COOLCTRL, 0)
        #settings.setGlobal('override_cool', 0)

    # Heat control
    if heat == 'on':
        controls.setPin(settings.PIN_HEATCTRL, 1)
        #settings.setGlobal('override_heat', 1)
    elif heat == 'off':
        controls.setPin(settings.PIN_HEATCTRL, 0)
        #settings.setGlobal('override_heat', 0)

    response['status'] = 'success'
    if override:
        response['override'] = override
    if fan:
        response['fan'] = fan
    if cool:
        response['cool'] = cool
    if heat:
        response['heat'] = heat

    return render_json(response)

def switch_temp(req):
    #if not req.user.is_authenticated():
    #    return render_json_err("You must be logged in to control the temperature!");

    response = {}
    target_f = req.GET.get('target_temp_f', None)
    target_c = req.GET.get('target_temp_c', None)

    # Convert it to celsius
    if target_f:
        # Make sure the user isn't an idiot and put in a letter for a number
        try:
            float(target_f)
        except ValueError:
            return render_json_err("The specified temperature is not a valid number!")

        target_c = shortcuts.temp_to_c(float(target_f))

    if target_c is not None:
        # Make sure the user isn't an idiot and put in a letter for a number
        try:
            float(target_c)
        except ValueError:
            return render_json_err("The specified temperature is not a valid number!")

        settings.set_target_temp(target_c)
        response['status'] = 'success'
        response['target_temp_c'] = target_c
    else:
        return render_json_err("No temperature has been specified.")

    return render_json(response)

def getLatestControlEvent(req):
    """
    Returns the last control event
    """
    
    response = {}
    evt = models.ControlEvent.objects.latest('time')
    
    if evt:
        response['status'] = 'success'
        response['evt'] = {
            'type': evt.type,
            'val': evt.val,
            'spec_data': evt.spec_data,
        }
    else:
        response['status'] = 'failed'
        response['message'] = 'No latest control event found!'
        response['evt'] = None

    return render_json(response)

def status(req):
    """
    Returns the current state of the controls (fan state, cooling, heating)
    """

    response = {}

    override = int(settings.getGlobal('override_auto', 0))
    fan = controls.readPin(settings.PIN_FANCTRL)
    cool = controls.readPin(settings.PIN_COOLCTRL)
    heat = controls.readPin(settings.PIN_HEATCTRL)

    response['status'] = 'success'
    response['override'] = override and 'on' or 'off'
    response['fan'] = fan and 'on' or 'off'
    response['cool'] = cool and 'on' or 'off'
    response['heat'] = heat and 'on' or 'off'

    return render_json(response)

def status_temp(req):
    """
    Returns the temperature status
    """

    response = {}
    response['target_temp_c'] = "%.2f" % settings.get_target_temp()
    response['target_temp_f'] = "%.2f" % shortcuts.temp_to_f(settings.get_target_temp())

    sensors = tempsensor.getSensorIDs()
    if len(sensors) > 0:
        sensor = tempsensor.getSensor(sensors[0])

        try:
            temp = sensor.read_temp()
            # Return the temp in both celsius and fahrenheit
            response['temp_c'] = "%.2f" % temp[0]
            response['temp_f'] = "%.2f" % temp[1]

            response['status'] = 'success'
        except tempsensor.CouldNotReadError as e:
            response['status'] = 'failed'
            response['message'] = 'Could not read temperature from sensor! (error reading from file)'

    else:
        response['status'] = 'failed'
        response['message'] = 'Could not read temperature from sensor! (no sensor detected)'

    return render_json(response)
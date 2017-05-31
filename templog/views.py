from django.shortcuts import render, Http404
from django.http.response import HttpResponse
from django.utils import timezone
import pytz
import thermoctrl

from common.shortcuts import render_json
from datetime import datetime, timedelta

from templog.models import Temp


def index(req):
    return render(req, 'templog/index.html')


def pngLastHrs(req, hours):
    raise Http404("aaaaaaaaaa")


def pgfLastHrs(req, hours):
    raise Http404("aaaaaaaaaa")


def getDataLastHrs(req, hours):
    response = {}

    tz = req.GET.get('timezone', None)
    if tz is not None:
        timezone.activate(tz)
    else:
        timezone.activate(thermoctrl.settings.TIME_ZONE)

    # Calculate the range for today
    end = timezone.now()
    start = end - timedelta(hours=int(hours))

    entries = Temp.objects.filter(time__range=[start, end])
    response['status'] = 'success'
    response['numEntries'] = len(entries)

    response['entries'] = []
    for e in entries:
        # Localize the time into the end user's timezone.
        zone = timezone.get_current_timezone()
        localTime = e.time.astimezone(zone)

        response['entries'].append({
            "time_h": localTime.hour,
            "time_m": localTime.minute,
            "temp": e.temp
        })

    timezone.deactivate()

    return render_json(response)


def getData(req):
    if req.method != 'GET':
        return render_json_err("Programmer error: No GET data supplied!")

    # Parse the datetime from JS (Date().toJSON())
    date_start = datetime.strptime(req.GET.get(
        'date_start', None), '%Y-%m-%dT%H:%M:%S.%fZ')
    date_end = datetime.strptime(req.GET.get(
        'date_end', None), '%Y-%m-%dT%H:%M:%S.%fZ')

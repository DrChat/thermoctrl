# Log temperature command
# Written by: Justin Moore
# Purpose: Logs the current temperature into a SQL database
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from templog.models import Temp
from common import tempsensor
from control import models

class Command(BaseCommand):
    help = 'Logs the current temperature and stores it in the SQL database'

    def handle(self, *args, **options):
        ids = tempsensor.getSensorIDs()
        if len(ids) <= 0:
            print("Uhoh! No sensor detected!")
            return

        # Just default to the first one detected
        sensor = tempsensor.getSensor(ids[0])
        readTemp = sensor.read_temp()

        # Create a model and store it in SQL.
        t = Temp()
        t.temp = readTemp[0]
        t.time = timezone.now()
        t.save()

        # Debug output (won't be logged by cron)
        print("Saved temperature (" + str(readTemp[1]) + " deg Fahrenheit)")
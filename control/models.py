from django.db import models

class GlobalSetting(models.Model):
    key = models.CharField(primary_key=True, max_length=255)
    type = models.IntegerField(default=0)
    value = models.TextField()

class ControlEvent(models.Model):
    time = models.DateTimeField()

    # TODO: Which user initiated the event, if any?

    EVENT_TYPE_FAN = 'F'
    EVENT_TYPE_COOL = 'C'
    EVENT_TYPE_HEAT = 'H'
    EVENT_TYPE_OVERRIDE = 'O'
    EVENT_TYPE_CHOICES = (
        (EVENT_TYPE_FAN, "Fan"),
        (EVENT_TYPE_COOL, "Cool"),
        (EVENT_TYPE_HEAT, "Heat"),
        (EVENT_TYPE_OVERRIDE, "Override"),
    )
    type = models.CharField(max_length=1, choices=EVENT_TYPE_CHOICES)
    val = models.IntegerField() # Target value (what it was switched to)
    spec_data = models.TextField(null=True) # Any special data associated with this control event

    def __unicode__(self):
        return "ControlEvent date:" + str(self.time) + " type:" + self.type + " val:" + str(self.val)

# Named weekly schedule preset
# Should we have a monthly schedule that sets these up? So we would have like summer/fall/winter schedules etc
class SchedulePreset(models.Model):
    name = models.TextField()

class ScheduleEntry(models.Model):
    preset = models.ForeignKey(SchedulePreset)
    # When this entry takes effect
    # These are defined as offsets from the beginning of the week, not exact datetimes!
    time_begin = models.DateTimeField()
    time_end = models.DateTimeField()

    # Target temperature at this time in degrees celsius
    target_temp = models.FloatField()
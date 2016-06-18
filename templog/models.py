from django.db import models

class Temp(models.Model):
    time = models.DateTimeField(auto_now_add=True, blank=True)
    temp = models.FloatField(default=0) # Temp. in celsius

    def __str__(self):
        return str(self.time) + " " + str(self.temp)

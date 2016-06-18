import os
import glob
import time
from exceptions import RuntimeError

from common import shortcuts

base_dir = '/sys/bus/w1/devices/'
#device_folder = glob.glob(os.path.join(base_dir, '28*'))[0]
#device_file = os.path.join(device_folder, 'w1_slave')

def getSensorIDs():
    folders = glob.glob(os.path.join(base_dir, '28*'))
    return folders

def getSensor(id):
    folder = os.path.join(base_dir, id)
    if not os.path.exists(folder):
        raise ValueError("Invalid ID " + id + "!")

    return Sensor(os.path.join(folder, 'w1_slave'))

class CouldNotReadError(RuntimeError):
    desc = ''

    def __init__(self, desc):
        self.desc = desc

    def __str__(self):
        return self.desc

    def __unicode__(self):
        return self.desc

class Sensor(object):
    __mFile = ''

    def __init__(self, file):
        self.__mFile = file

    def read_temp_raw(self):
        f = open(self.__mFile, 'r')
        lines = f.readlines()
        f.close()

        return lines

    def read_temp(self):
        """
        read_temp
        Reads the temperature from the temperature sensor.
        Returns a tuple with (degrees celsius, degrees fahrenheit)
        """
        lines = self.read_temp_raw()

        # Keep track of the number of tries so we don't go into an infinite loop.
        tries = 0
        while lines[0].strip()[-3:] != 'YES':
            if tries > 3:
                raise CouldNotReadError("NO detected from device (tried to read 5 times)!")

            time.sleep(0.1)
            tries += 1
            lines = self.read_temp_raw()

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = shortcuts.temp_to_f(temp_c)
            return temp_c, temp_f

#def read_temp_raw():
#    f = open(device_file, 'r')
#    lines = f.readlines()
#    f.close()
#    return lines
#
#def read_temp():
#    """
#    read_temp
#    Reads the temperature from the temperature sensor.
#    Returns a tuple with (degrees celsius, degrees fahrenheit)
#    """
#    lines = read_temp_raw()
#    while lines[0].strip()[-3:] != 'YES':
#        time.sleep(0.2)
#        lines = read_temp_raw()
#
#    equals_pos = lines[1].find('t=')
#    if equals_pos != -1:
#        temp_string = lines[1][equals_pos+2:]
#        temp_c = float(temp_string) / 1000.0
#        temp_f = temp_c * 9.0 / 5.0 + 32.0
#        return temp_c, temp_f
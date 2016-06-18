#!/usr/bin/env python
import os
import sys
#import ptvsd

# Enable ptvs attachment
#ptvsd.enable_attach(secret='hi')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thermoctrl.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

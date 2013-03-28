#!/usr/bin/env python
import getopt
import os
import sys

if __name__ == "__main__":

    if True:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "upcms.settings_development")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "upcms.settings_production")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

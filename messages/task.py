import urllib2
from upcms import settings_production as settings
import sys

__author__ = 'cysnake4713'

if __name__ == "__main__":

    TYPE = sys.argv[1]
    urllib2.urlopen(settings.CMS_HOME + '/message/reload/%s/' % TYPE)

import urllib2
import sys

__author__ = 'cysnake4713'
CMS_HOME = 'http://127.0.0.1:8001'

if __name__ == "__main__":

    TYPE = sys.argv[1]
    connection = urllib2.urlopen(CMS_HOME + '/message/reload/%s/' % TYPE)
    connection.close()

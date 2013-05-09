__author__ = 'cysnake4713'

import urllib2
import simplejson
from cookielib import CookieJar

url = 'http://localhost:8069/web/session/authenticate'
host = 'http://localhost:8069'
def test():
    # data = {"jsonrpc": "2.0", "method": "call",
    #         "params": {"session_id": None, "context": {}}, "id": "r0"}
    cj = CookieJar()
    data = {"jsonrpc": "2.0", "method": "call",
            "params": {"db": "develop", "login": "admin", "password": "admin", "base_location": "http://localhost:8069",
                       "session_id": None, "context": {}}, "id": "r0"}

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    # hostcon = urllib2.urlopen(host)
    request = urllib2.Request(url, simplejson.dumps(data), {'Content-Type': 'application/json'})
    response = urllib2.urlopen(request)
    return response

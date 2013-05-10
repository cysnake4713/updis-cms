import json

__author__ = 'cysnake4713'

import urllib2
from cookielib import CookieJar
import upcms.settings as settings

# url = 'http://localhost:8069/web/session/authenticate'
HOST = 'http://%s:%d' % (settings.ERP_HOST, settings.ERP_PORT)


# def test():
#     # data = {"jsonrpc": "2.0", "method": "call",
#     #         "params": {"session_id": None, "context": {}}, "id": "r0"}
#     cj = CookieJar()
#     data = {"jsonrpc": "2.0", "method": "call",
#             "params": {"db": "develop", "login": "admin", "password": "admin", "base_location": "http://localhost:8069",
#                        "session_id": None, "context": {}}, "id": "r0"}
#
#     opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#     urllib2.install_opener(opener)
#     # hostcon = urllib2.urlopen(host)
#     request = urllib2.Request(url, simplejson.dumps(data), {'Content-Type': 'application/json'})
#     response = urllib2.urlopen(request)
#     # print response.read()
#
#     request2 = urllib2.Request('http://localhost:8069/web/session/get_session_info', simplejson.dumps(
#         {"jsonrpc": "2.0", "method": "call", "params": {"session_id": None, "context": {}}, "id": "r0"}),
#                                {'Content-Type': 'application/json'})
#
#     return response

# class ERPUser:
#     def __init__(self, uid, name):
#         self.uid = uid
#         self.name = name


def _send_json_info(url, data, request):
    json_request = urllib2.Request(url, json.dumps(data), {'Content-Type': 'application/json'})
    cookies = 'sid=%s; instance0|session_id=%s' % (
        request.COOKIES.get('sid'), request.COOKIES.get('instance0|session_id'))
    json_request.add_header('Cookie', cookies)
    return urllib2.urlopen(json_request)


def _get_session_id(request):
    session_id = None
    if request.COOKIES.get('sid') and request.COOKIES.get('instance0|session_id'):
        session_id = str(request.COOKIES.get('instance0|session_id'))
        session_id = session_id[3:len(session_id) - 3]
        session_id = session_id and session_id or None
    return session_id


def _user_info(uid, username):
    return {'uid': uid, 'username': username}


def get_session_info(request):
    session_id = _get_session_id(request)
    # if login, get user info
    if session_id:
        get_session_data = {"jsonrpc": "2.0", "method": "call", "params": {"session_id": session_id, "context": {}},
                            "id": "r0"}
        response = _send_json_info(HOST + '/web/session/get_session_info', get_session_data, request)
        json_response = json.loads(response.read())
        if json_response['result']:
            request.session['erp_user'] = _user_info(json_response['result']['uid'],
                                                     json_response['result']['username'])
        else:
            request.session['erp_user'] = None
            # no session_id means not login.
    else:
        request.session['erp_user'] = None


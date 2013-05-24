import json

__author__ = 'cysnake4713'

import urllib2
import upcms.settings as settings

HOST = settings.ERP_HOME


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


def _user_info(uid, username, context):
    return {'uid': uid, 'username': username, 'context': context}


def login(request, username, password):
    login_data = {"jsonrpc": "2.0", "method": "call",
                  "params": {"db": settings.ERP_DATABASE, "login": username, "password": password,
                             "base_location": HOST,
                             "session_id": None, "context": {}}, "id": "r0"}

    response = _send_json_info(HOST + '/web/session/authenticate', login_data, request)
    json_response = json.loads(response.read())
    if json_response['result']:
        if json_response['result']['uid']:
            cookie_header = response.info().getheader('Set-Cookie')
            res = cookie_header.split(';')[0].split('=')
            return (res[1], json_response['result']['session_id'])
    return None


def get_session_info(request):
    session_id = _get_session_id(request)
    # if login, get user info
    if session_id:
        get_session_data = {"jsonrpc": "2.0", "method": "call", "params": {"session_id": session_id, "context": {}},
                            "id": "r0"}
        response = _send_json_info(HOST + '/web/session/get_session_info', get_session_data, request)
        json_response = json.loads(response.read())
        if json_response['result'] and json_response['result']['username']:
            request.session['erp_user'] = _user_info(json_response['result']['uid'],
                                                     json_response['result']['username'],
                                                     json_response['result']['user_context'])
        else:
            request.session['erp_user'] = None
            # no session_id means not login.
    else:
        request.session['erp_user'] = None


def logout(request):
    session_id = _get_session_id(request)
    if session_id:
        logout_data = {'params': {'context': request.session['erp_user']['context'],
                                  'session_id': session_id}, 'jsonrpc': '2.0', 'method': 'call',
                       'id': 'r27'}
        response = _send_json_info(HOST + '/web/session/destroy', logout_data, request)
        json_response = json.loads(response.read())
        print(json_response)
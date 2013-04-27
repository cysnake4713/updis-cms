from django.utils.functional import SimpleLazyObject
from openerplib import get_connection

from upcms import settings

__author__ = 'Zhou Guangwen'


def get_erpsession(request):
    session = request.session
    # if not session.get('erpsession',False):
    conn = get_connection(settings.ERP_HOST, port=settings.ERP_PORT, database=settings.ERP_DATABASE,
                          login=settings.ERP_LOGIN, password=settings.ERP_PASSWORD)
    session['erpsession'] = conn
    return session['erpsession']


def get_user_erpsession(request):
    session = request.session
    # if not session.get('erpsession',False):
    attributes = request.session.get("attributes", None)
    if attributes:
        conn = get_connection(settings.ERP_HOST, port=settings.ERP_PORT, database=attributes['db'],
                              login=attributes['username'], password=attributes['password'])
    else:
        #TODO
        conn = get_connection(settings.ERP_HOST, port=settings.ERP_PORT, database=settings.ERP_DATABASE,
                              login=settings.ERP_LOGIN, password=settings.ERP_PASSWORD)
    session['usererpsession'] = conn
    return session['usererpsession']


class ERPSessionMiddleware(object):
    def process_request(self, request):
        assert hasattr(request,
                       'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        # request.erpsession = SimpleLazyObject(lambda: get_erpsession(request))
        request.erpsession = SimpleLazyObject(lambda: get_erpsession(request))
        request.usererpsession = SimpleLazyObject(lambda: get_user_erpsession(request))
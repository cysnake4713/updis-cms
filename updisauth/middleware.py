__author__ = 'cysnake4713'
import authenticate as auth


class ERPAuthMiddleWare(object):
    def process_request(self, request):
        auth.get_session_info(request)

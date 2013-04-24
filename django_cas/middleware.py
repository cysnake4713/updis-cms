"""CAS authentication middleware"""

from urllib import urlencode

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import login, logout
from django.core.urlresolvers import reverse

from django_cas.views import login as cas_login, logout as cas_logout, _login_url, _redirect_url, _service_url
from messages.middleware import get_erpsession

__all__ = ['CASMiddleware']

class CASMiddleware(object):
    """Middleware that allows CAS authentication on admin pages"""

    def process_request(self, request):
        """Checks that the authentication middleware is installed"""

        error = ("The Django CAS middleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
                 "setting to insert 'django.contrib.auth.middleware."
                 "AuthenticationMiddleware'.")
        assert hasattr(request, 'user'), error
        if request.path.startswith("/accounts"):
            return
        cas_ctx = request.session.get("cas",None)
        if cas_ctx:
            from django.contrib import auth
            user = auth.authenticate(ticket=cas_ctx['ticket'], service=cas_ctx['service'], request=request)
            if user is not None:
                pass
            else:
                request.session['cas']=None
                request.erpsession =  get_erpsession(request)
                request.session['erpsession']=request.erpsession
                auth.logout(request)

        else:
            next_page = _redirect_url(request)
            return HttpResponseRedirect(_login_url(_service_url(request, next_page)))


    def process_view(self, request, view_func, view_args, view_kwargs):
        """Forwards unauthenticated requests to the admin page to the CAS
        login URL, as well as calls to django.contrib.auth.views.login and
        logout.
        """

        if view_func == login:
            return cas_login(request, *view_args, **view_kwargs)
        elif view_func == logout:
            return cas_logout(request, *view_args, **view_kwargs)

        if settings.CAS_ADMIN_PREFIX:
            if not request.path.startswith(settings.CAS_ADMIN_PREFIX):
                return None
        elif not view_func.__module__.startswith('django.contrib.admin.'):
            return None

        if request.user.is_authenticated():
            if request.user.is_staff:
                return None
            else:
                error = ('<h1>Forbidden</h1><p>You do not have staff '
                         'privileges.</p>')
                return HttpResponseForbidden(error)
        params = urlencode({REDIRECT_FIELD_NAME: request.get_full_path()})
        return HttpResponseRedirect(reverse(cas_login) + '?' + params)

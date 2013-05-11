from upcms import settings

__author__ = 'cysnake4713'

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from messages.forms import LoginForm
import authenticate as auth


def erp_logout(request, redirect_url):
    auth.logout(request)
    response = HttpResponseRedirect(redirect_url)
    if settings.ERP_DOMAIN == 'localhost':
        response.set_cookie('instance0|session_id', '%%22%s%%22' % "")
    else:
        response.set_cookie('instance0|session_id', '%%22%s%%22' % "", domain=settings.ERP_DOMAIN)
    return response


def erp_login(request, redirect_url):

    #check session, if is login, redirect to redirect_url
    if request.session['erp_user'] is not None:
        return HttpResponseRedirect(redirect_url)

    #else do login
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']
            # try login
            result = auth.login(request, username, password)
            if result:
                response = HttpResponseRedirect(redirect_url)
                if settings.ERP_DOMAIN == 'localhost':
                    response.set_cookie('sid', result[0])
                    response.set_cookie('instance0|session_id', '%%22%s%%22' % result[1])
                else:
                    response.set_cookie('sid', result[0], domain=settings.ERP_DOMAIN)
                    response.set_cookie('instance0|session_id', '%%22%s%%22' % result[1], domain=settings.ERP_DOMAIN)
                return response
            else:
                return render_to_response("updisauth/login.html", {'form': form},
                                          context_instance=RequestContext(request))
    else:
        form = LoginForm()
    return render_to_response("updisauth/login.html", {'form': form}, context_instance=RequestContext(request))

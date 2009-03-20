# -*- coding: utf-8 -*-
"""
Views for handling OpenID authorization and registration
"""

from openid.consumer import consumer, discover
from openid.extensions import sreg #SRegRequest, SRegResponse
from openid.extensions import ax
from openid import oidutil
import re
from urlparse import urlsplit
import time
import pickle
from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from cargo.auth_openid.forms import OpenIDLoginForm#, OpenIDRegistrationForm
from cargo.auth_openid.models import OpenID
from cargo.auth_openid.util import uri_to_username, render_to, str_to_class
from cargo.auth_openid import settings as app_settings

RegistrationForm = str_to_class(app_settings.REGISTRATION_FORM)

# logging
if app_settings.LOGFILE:
    def log_func(message, level=0):
        ts = datetime.now().strftime('%Y-%m-%d/%H:%M:%S')
        open(app_settings.LOGFILE, 'a').write(u'%s %s\n' % (ts, message))
    oidutil.log = log_func


def build_redirect_url(request, default_url=None):
    """
    Return url saved to session.

    If saved url is not safe then return default url.
    """

    if default_url is None:
        default_url = app_settings.REGISTRATION_REDIRECT_URL
    redirect_url = request.session.get('login_redirect_url')
    if not redirect_url or '//' in redirect_url or ' ' in redirect_url:
        redirect_url = default_url
    del request.session['login_redirect_url']
    return redirect_url


def message(msg):
    """
    Shortcut that prepare data for message view.
    """

    return {'TEMPLATE': 'auth_openid/message.html', 'message': msg}


def login_ctx(request, provider=None):
    """
    If OpenID url was submitted then start OpenID authentication
    else display OpenID authentication form
    """

    post = request.POST.copy()
    initial = {}
    if provider == 'google':
        google_uri = 'https://www.google.com/accounts/o8/id'
        post['openid_url'] = google_uri
        initial['openid_url'] = google_uri

        request.method = 'POST'
        request.POST = post
    
    if provider == 'yahoo':
        google_uri = 'http://yahoo.com'
        post['openid_url'] = google_uri
        initial['openid_url'] = google_uri

        request.method = 'POST'
        request.POST = post

    if 'POST' == request.method:
        form = OpenIDLoginForm(post, post=request.POST)
    else:
        form = OpenIDLoginForm(initial=initial)
    error = ''
    
    request.session['login_redirect_url'] = request.GET.get('next')

    if form.is_valid():
        openid_url = form.cleaned_data['openid_url']
        return_to = request.build_absolute_uri(reverse('openid_complete'))
        request.session['openid_return_to'] = return_to
        client = consumer.Consumer(request.session, None)
        try:
            if app_settings.PROFILE_DETAILS:
                auth_req = client.begin(openid_url)
                auth_req.addExtension(sreg.SRegRequest(required=app_settings.PROFILE_DETAILS))

                ax_msg = ax.FetchRequest()
                for detail in app_settings.PROFILE_DETAILS:
                    ax_msg.add(ax.AttrInfo(app_settings.AX_URIS[detail], required=True))
                auth_req.addExtension(ax_msg)

            redirect_url = auth_req.redirectURL(realm='http://' + request.get_host(),
                                                return_to=return_to)
            return HttpResponseRedirect(redirect_url)

        except discover.DiscoveryFailure, ex:
            error = _('Could not find OpenID server')
            form.errors['openid_url'] = [error]

    return {'form': form,
            'error': error,
            }
login = render_to('auth_openid/login.html')(login_ctx)

@render_to('auth_openid/login.html')
def complete(request):
    """
    Complete OpenID authorization process.
    If OpenID URL was successfuly authenticated:
     * if user with such URL exists then login as this user
     * if no user with such URL exists then redirect to registration form
     * if no user with such URL exists and current user is authenticated then
       assign OpenID url to this user
    """

    registration_redirect = getattr(settings, 'AUTH_OPENID_REGISTRATION_REDIRECT_URL',
        reverse('auth_openid.views.manage_urls'))

    error = ''
    client = consumer.Consumer(request.session, None)

    #import pdb; pdb.set_trace()
    #args = dict((x, y[0]) for x, y in request.GET.iteritems())
    args = dict(request.GET.items())
    if 'POST' == request.method:
        args.update(request.POST)
    resp = client.complete(args, request.session.get('openid_return_to'))

    try:
        del request.session['openid_return_to']
    except KeyError:
        pass
    if resp.status == consumer.CANCEL:
        error = u'You have cancelled OpenID authorization'
    elif resp.status == consumer.FAILURE:
        error = u'OpenID authorization failed. Reason: %s' % resp.message
    elif resp.status == consumer.SUCCESS:
        if request.user.is_authenticated():
            try:
                user = OpenID.objects.get(url=resp.identity_url).user
            except OpenID.DoesNotExist:
                pass
            else:
                return message(u'Этот OpenID URL уже привязан к аккаунту %s' % user.username)
            OpenID(user=request.user, url=resp.identity_url).save()
            return HttpResponseRedirect(registration_redirect)
        else:
            user = auth.authenticate(openid_url=resp.identity_url)
            if user:
                auth.login(request, user)
                error = u'You have saccessfully authorized via OpenID'
                redirect_url = build_redirect_url(request, getattr(settings, 'LOGIN_REDIRECT_URL', None))
                return HttpResponseRedirect(redirect_url)
            else:
                request.session['authenticated_openid_url'] = resp.identity_url
                sreg_resp = sreg.SRegResponse.fromSuccessResponse(resp)
                request.session['sreg_resp'] = pickle.dumps(sreg_resp)

                ax_resp = ax.FetchResponse.fromSuccessResponse(resp)
                request.session['ax_resp'] = pickle.dumps(ax_resp)
                return HttpResponseRedirect(reverse('openid_registration'))
    else:
        error = 'OpenID authorization failed'
    form = OpenIDLoginForm()
    return {'form': form,
            'error': error}

@render_to('auth_openid/registration.html')
def registration(request, form_class=RegistrationForm):
    """
    Handle registration new user with given openid_url in session
    """
    
    #request.session['authenticated_openid_url'] = 'http://%d.foo.com' % int(time.time())
    openid_url = request.session.get('authenticated_openid_url')

    if not openid_url:
        return HttpResponseRedirect(reverse('openid_login'))

    kwargs = {'openid_url': openid_url}

    if 'POST' == request.method:
        form = form_class(request.POST, **kwargs)
    else:
        details = {}

        def get_name(name):
            return app_settings.PROFILE_DETAILS_MAPPING.get(name, name)

        if 'sreg_resp' in request.session:
            sreg_resp = pickle.loads(request.session['sreg_resp'])
            if sreg_resp:
                for detail in app_settings.PROFILE_DETAILS: 
                    details[get_name(detail)] = sreg_resp.get(detail, '')

        if 'ax_resp' in request.session:
            ax_resp = pickle.loads(request.session['ax_resp'])
            if ax_resp:
                for detail in app_settings.PROFILE_DETAILS:
                    if not details.get(detail):
                        details[get_name(detail)] = ax_resp.getSingle(app_settings.AX_URIS[detail], '')
        form = form_class(initial=details, **kwargs)

    if form.is_valid():
        user = form.save()
        user = auth.authenticate(openid_url=openid_url)
        auth.login(request, user)
        del request.session['authenticated_openid_url']

        redirect_url = build_redirect_url(request)
        return HttpResponseRedirect(redirect_url)
    return {'form': form,
            'openid_url': openid_url,
            }


@login_required
@render_to('auth_openid/manage_urls.html')
def manage_urls(request):
    openids = OpenID.objects.filter(user=request.user)
    return {'openids': openids,
            }


@login_required
@render_to(None)
def delete(request, openid_url):
    urls = dict([(x.url, x) for x in OpenID.objects.filter(user=request.user)])
    print urls
    if openid_url not in urls:
        return message(u'Неверный OpenID аккаунт')
    if len(urls) == 1 and not request.user.has_usable_password():
        return message(u'Перед удалением единственного OpenID аккаунта вы должны задать пароль для авторизации по логину/паролю')
    else:
        urls[openid_url].delete()
        return message(u'OpenID аккаунт удалён')


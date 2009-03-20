import re
from time import time

from django import forms
from django.conf import settings

from cargo.auth_openid.util import uri_to_username, str_to_class
from cargo.auth_openid.models import OpenID
from cargo.auth_openid import settings as app_settings

UserModel = str_to_class(app_settings.USER_MODEL)

#if hasattr(settings, 'AUTH_OPENID_USERNAME_CLASS'):
    #cls = settings.AUTH_OPENID_USERNAME_CLASS
#else:
    #cls = 'auth.models.kk
#User._meta.get_field('username').formfield()

def username_field():
    #username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        #help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        #error_message = _("This value must contain only letters, numbers and underscores."))

    username = forms.CharField()
    return username

class OpenIDLoginForm(forms.Form):
    openid_url = forms.CharField(u'OpenID URL')

    def __init__(self, *args, **kwargs):
        self.post = kwargs.pop('post', {})
        kwargs['auto_id'] = '%s'
        super(OpenIDLoginForm, self).__init__(*args, **kwargs)

    #def clean_openid_url(self):
        #return self.cleaned_data['openid_url']

class OpenIDRegistrationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.require_email = getattr(settings, 'OPENID_REQUIRE_EMAIL', True),
        self.unique_email = getattr(settings, 'OPENID_UNIQUE_EMAIL', True),
        self.require_username = getattr(settings, 'OPENID_REQUIRE_USERNAME', True),

        if self.require_email:
            self.base_fields['email'] = UserModel._meta.get_field('email').formfield(required=True)
        if self.require_username:
            self.base_fields['username'] = username_field()
        self.openid_url = kwargs.pop('openid_url')
        super(self.__class__, self).__init__(*args, **kwargs)

    def clean_email(self):
        if 'email' in self.cleaned_data:
            email = self.cleaned_data['email']
            try:
                UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                return email
            else:
                raise forms.ValidationError(u'This email is already registered')

    def clean_username(self):
        if 'username' in self.cleaned_data:
            username = self.cleaned_data['username']
            #if not re.search(r'^[a-z0-9_]+$', username, re.I):
                #raise forms.ValidationError('Restricted symbols in username')
            try:
                UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return username
            else:
                raise forms.ValidationError(u'This username is already registered')

    def clean(self):
        if not self.require_username:
            self.cleaned_data['username'] = uri_to_username(self.openid_url)
        if not self.require_email:
            self.cleaned_data['email'] = ''
        return self.cleaned_data

    def save(self):
        user = UserModel.objects.create_user(self.cleaned_data['username'],
                                        self.cleaned_data['email'])
        user.is_active = True
        user.save()
        OpenID(user=user, url=self.openid_url).save()
        return user

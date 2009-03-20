from django.conf import settings

REGISTRATION_REDIRECT_URL = getattr(settings, 'AUTH_OPENID_REGISTRATION_REDIRECT_URL', '/')
USER_MODEL = getattr(settings, 'AUTH_OPENID_USER_MODEL', 'django.contrib.auth.models.User')

REGISTRATION_FORM = getattr(settings,
    'AUTH_OPENID_REGISTRATION_FORM', 'cargo.auth_openid.forms.OpenIDRegistrationForm')
LOGFILE = getattr(settings, 'AUTH_OPENID_LOGFILE', None)

# OpenID profile attributes
# SREG: http://openid.net/specs/openid-simple-registration-extension-1_0.html
# AX: http://openid.net/specs/openid-attribute-exchange-1_0.html

SREG_FIELDS = [
    'nickname', 'email', 'fullname', 'dob', 'gender',
    'postcode', 'country', 'language', 'timezone']

PROFILE_DETAILS = set(getattr(settings, 'AUTH_OPENID_PROFILE_DETAILS', []))
for detail in list(PROFILE_DETAILS):
    if not detail in SREG_FIELDS:
        PROFILE_DETAILS.remove(detail)

PROFILE_DETAILS_MAPPING = getattr(settings,
    'AUTH_OPENID_PROFILE_DETAILS_MAPPING', {'nickname': 'username'})


# This dict contains mapping of SREG fields to AX uris
# http://www.axschema.org/types/
AX_URIS = {
    'nickname': 'http://axschema.org/namePerson/friendly',
    'email': 'http://axschema.org/contact/email',
    'fullname': 'http://axschema.org/namePerson',
    'dob': 'http://axschema.org/birthDate',
    'gender': 'http://axschema.org/person/gender',
    'postcode': 'http://axschema.org/contact/postalCode/home',
    'country': 'http://axschema.org/contact/country/home',
    'language': 'http://axschema.org/pref/language',
    'timezone': 'http://axschema.org/pref/timezone',
}

from datetime import datetime
from django.core.cache import cache
from django.conf import settings

from cargo.auth_openid.models import OpenID
from cargo.auth_openid.util import str_to_class
from cargo.auth_openid import settings as app_settings

UserModel = str_to_class(app_settings.USER_MODEL)

class OpenIDMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            ids = OpenID.objects.filter(user=request.user)
            request.user.openid_list = ids
        else:
            request.user.openid_list = []
        return None


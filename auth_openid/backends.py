from django.contrib.auth.models import User

from cargo.auth_openid.models import OpenID

class OpenIDBackend(object):
    def authenticate(self, openid_url=None):
        if openid_url:
            try:
                user = OpenID.objects.get(url=openid_url).user
                return user
            except OpenID.DoesNotExist:
                return None
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None



from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from cargo.auth_openid import settings as app_settings
from cargo.auth_openid.util import str_to_class

UserModel = str_to_class(app_settings.USER_MODEL)

class OpenID(models.Model):
    user = models.ForeignKey(UserModel)
    url = models.CharField(u'OpenID URL', max_length=255, unique=True)

    def __unicode__(self):
        return self.url

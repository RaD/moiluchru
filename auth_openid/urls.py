from django.conf.urls.defaults import *

from cargo.auth_openid import views

urlpatterns = patterns('',
    url(r'^login/$', views.login, {'provider': None}, name='openid_login'),
    url(r'^login/(?P<provider>.*)/$', views.login, name='openid_login_custom'),
    url(r'^complete/$', views.complete, name='openid_complete'),
    url(r'^registration/$', views.registration, name='openid_registration'),
    url(r'^manage_urls/$', views.manage_urls),
    url(r'^delete/(?P<openid_url>.+)/$', views.delete),
)

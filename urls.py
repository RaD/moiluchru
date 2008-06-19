from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Интерфейс администратора
    (r'^admin/', include('django.contrib.admin.urls')),

    # Управление авторизацией пользователей
    (r'^accounts/login', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
     {'next_page': '/accounts/login/'}),

    # Подключение схем URL
    (r'^djangobook/', include('cargo.djangobook.urls')),
    (r'^shop/', include('cargo.shop.urls')),
)

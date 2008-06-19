# файл с трансляциями

from django.contrib.syndication.feeds import Feed
from django.core.exceptions import ObjectDoesNotExist
from cargo.djangobook.models import News

class LatestNews(Feed):
    # заголовок трансляции
    title = "DjangoBook по-русски"

    # описание трансляции
    description = "Самые свежие новости о жизни русской версии DjangoBook."

    # ссылка на страницу с новостями
    link = "/news/"

    # последние пять новостей
    def items(self):
        return News.objects.order_by('-datetime')[:5]

    

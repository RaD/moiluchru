# -*- coding: utf-8 -*-

import django
#from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import TemplateDoesNotExist, RequestContext
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from cargo import settings
from cargo.djangobook.models import News, Text, Claims, ClaimStatus

from cargo.snippets import render_to, paged

import zipfile, re, os
from datetime import datetime, timedelta

news_info_extra = {
    'spelling_error_count': lambda: Claims.objects.count(),
    'django_version': django.get_version()
}

news_info = {
    'queryset': News.objects.order_by('-datetime')[:5],
    'template_name': 'djangobook/news-list.html',
    'extra_context': news_info_extra # дополнительный контекст
}

def context_processor(request):
    """ Контекст страницы. """
    return {'user': request.user, 'debug': settings.DEBUG,
            'django_version': django.get_version(),
            'spelling_error_count_pending': get_claims_count_by_status(1),
            'spelling_error_count_assigned': get_claims_count_by_status(2),
            'spelling_error_count_fixed': get_claims_count_by_status(3),
            'spelling_error_count_invalid': get_claims_count_by_status(4)
            }

def get_claims_count_by_status(code):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute ('select id from djangobook_claimstatus where status=%i and \
    applied in (select max(applied) from djangobook_claimstatus group by claim_id)' % int(code))
    return int(cursor.rowcount)

def get_news_statistics():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(' '.join(['select year(datetime) y, month(datetime) m,'
                             'count(month(datetime)) q, min(id) id',
                             'from djangobook_news group by month(datetime), year(datetime)',
                             'order by 1 desc,2 desc']));
    return cursor.fetchall()

def get_toc(version):
    zip = settings.DJANGOBOOK_PAGE_ZIP.get(version)
    try:
        z = zipfile.ZipFile(zip)
        toc = eval("%s" % z.read('toc.py'))
	z.close()
    except (IOError, KeyError):
        toc = {}
    return toc

def prepare_toc(toc, chapter=None, section=None):
    chapters = []
    sections = []
    for item in toc.get('chapters'):
        # для каждой главы получаем её номер, её секции и генерируем url
        r = re.match(r'^.*\.chap(?P<number>\d+)$', item[0])
        url = '#'
        if not r:
            print 'ERROR' # FIXME: сделать исключение!
        url = 'ch%s.html' % (r.group('number'),)
        chapters.append([url, item[1]]) # id and title

        if chapter:
            if chapter != 'ap' and chapter == r.group('number'):
                # если это глава и её номер совпадает с выбранной, то сохраняем список секций
                for s in item[2]:
                    index = item[2].index(s)+1
                    if index == 1:
                        sections.append(('ch%s.html#%s' % (chapter, s[0]), s[1]))
                    else:
                        sections.append(('ch%ss%02i.html' % (chapter, index), s[1]))

    for item in toc.get('appendixes'):
        # для каждого приложения получаем его букву и генерируем url
        r = re.match(r'^.*\.appendix_(?P<letter>[a-z])$', item[0])
        url = '#'
        if not r: 
            print 'ERROR' # FIXME: сделать исключение!
        url = 'ap%s.html' % (r.group('letter'),)
        curr_url = 'ap%s.html' % (section, )
        chapters.append([url, item[1]]) # id and title
    return {'chapters': chapters, 'sections': sections, 'url': url, 'chapter_url': 'ch%s.html' % (chapter,)}  

def get_page_from_zip(page, version):
    if not settings.DJANGOBOOK_PAGE_ZIP:
        message = _(u'Did you forget to fill the `DJANGOBOOK_PAGE_ZIP` variable at `settings.py`?')
        return None
    zip = settings.DJANGOBOOK_PAGE_ZIP.get(version)
    if not os.access(zip, os.R_OK):
        message = _(u'Tell to the site administrator that he has been forgot to grant access right on the archive file.')
        return None
    try:
        z = zipfile.ZipFile(zip)
        content = z.read(page)
	z.close()
    except (IOError, KeyError):
        raise TemplateDoesNotExist(template_name)
    return content

@render_to('djangobook/page.html', context_processor)
def show_db_page(request, chapter=None, section=None):
    """Show book's page."""
    if request.session.test_cookie_worked():
        if not 'version' in request.session:
            request.session['version'] = '1'
    else:
        request.session.set_test_cookie()

    version = request.session.get('version', '1')

    if chapter == 'ap':
        page = 'ap%s.html' % section
        title = u'Приложение %s' % section
    elif chapter is None and section is None:
        page = 'index.html'
        title = u'Первая страница'
    elif section is None:
        page = 'ch%s.html' % chapter
        title = u'Глава %i' % int(chapter)
    else:
        page = 'ch%ss%s.html' % (chapter, section)
        title = u'Глава %i, раздел %i' % (int(chapter), int(section))
    context = {'page_title': u'%s : DjangoBook v%s.0' % (title, version),
               'version': version,
               'page_content': get_page_from_zip(page, version),
               'readers_count': len(request.session.get('readers', {}))}
    if page == 'index.html':
        context.update({'news_list': News.objects.order_by('-datetime')[:5]})
    else:
        context.update({'toc': prepare_toc(get_toc(version), chapter, section)})
    return context
    
def user_claims(request):
    """ This function handles users' claims on spelling error.
    It saves all information into Claims model. It doesn't check
    the fields' length. """
    if (request.is_ajax()):
        record = Claims(ctx_left=request.POST.get('ctx_left', ''),
                        selected=request.POST.get('selected', 'None'),
                        ctx_right=request.POST.get('ctx_right', ''),
                        email=request.POST.get('email', 'unknown@hz.ru'),
                        notify='true'==request.POST.get('notify', None),
                        comment=request.POST.get('comment', 'No comments...'),
                        url=request.META.get('HTTP_REFERER', ''),
                        datetime=datetime.now())
        record.save()
        status = ClaimStatus(claim=record, status=1, applied=datetime.now())
        status.save()
        return HttpResponse('<result>ok</result>', mimetype="text/xml")
    else:
        return HttpResponse('<result>error</result>', mimetype="text/xml")

def claims_penging(request):
    """ Функция возвращает количество жалоб в очереди. """
    if request.is_ajax():
        return HttpResponse(''.join(['<result><code>200</code><desc>success</desc>',
                                     '<pending>%i</pending>' % get_claims_count_by_status(1),
                                     '<assigned>%i</assigned>' % get_claims_count_by_status(2),
                                     '<fixed>%i</fixed>' % get_claims_count_by_status(3),
                                     '<invalid>%i</invalid>' % get_claims_count_by_status(4),
                                     '<readers>%i</readers></result>' % 1]),
                            mimetype="text/xml")
    else:
        return HttpResponse('<result><code>400</code><desc>it must be ajax call</desc></result>', 
                            mimetype="text/xml")

def version(request):
    if request.is_ajax():
        request.session['version'] = '%s' % request.POST.get('version', '1')
        return HttpResponse('<version>%s</version>' % request.session['version'],
                            mimetype="text/xml")
    else:
        return HttpResponse('<result><code>400</code><desc>it must be ajax call</desc></result>', 
                            mimetype="text/xml")

@render_to('djangobook/news.html', context_processor)
def show_news_page(request, news_id=None):
    """Show news' page."""
    if not news_id:
        return HttpResponseRedirect('/djangobook/archive/')
    month_names = [u'Январь', u'Февраль', u'Март', u'Апрель', u'Май', u'Июнь', 
                   u'Июль', u'Август', u'Сентябрь', u'Октябрь', u'Ноябрь', u'Декабрь']
    news = News.objects.order_by('-datetime')
    news_statistics = get_news_statistics()
    news_curr = news.get(id=news_id)
    year_curr = datetime.today().year
    return {'page_title': u'Новость: %s : DjangoBook v1.0' % (news_curr.title,),
            'current_year': year_curr,
            'news_curr': news_curr,
            'year_list': set([n[0] for n in news_statistics]),
            'month_list': [(n[1], month_names[n[1]-1], n[2]) \
                               for n in news_statistics if n[0] == year_curr]}

@render_to('djangobook/archive.html', context_processor)
def show_archive_page(request, year=None, month=None):
    """Show news' page."""
    if not year: year = datetime.today().year
    if not month: month = datetime.today().month
    month_names = [u'Январь', u'Февраль', u'Март', u'Апрель', u'Май', u'Июнь', 
                   u'Июль', u'Август', u'Сентябрь', u'Октябрь', u'Ноябрь', u'Декабрь']
    news = News.objects.order_by('-datetime')
    news_statistics = get_news_statistics()
    news_list = news.filter(datetime__year=int(year), datetime__month=int(month))
    return {'page_title': u'Архив: %s %s : DjangoBook v1.0' % (month_names[int(month)-1], year),
            'current_year': int(year),
            'current_month': int(month),
            'news_list': news_list,
            'year_list': set([n.datetime.year for n in news]),
            'month_list': [(n[1], month_names[n[1]-1], n[2]) for n in news_statistics if n[0] == int(year)]}

@render_to('djangobook/text.html', context_processor)
def text(request, label=None):
    o = Text.objects.get(label=label)
    return {'page_title': u'Заметка с меткой: %s : DjangoBook v1.0' % (label,),
            'news_list': News.objects.order_by('-datetime')[:5],
            'page_content': o.text}

@render_to('djangobook/search.html', context_processor)
def search(request):
    return {'page_title': u'Результаты поиска: %s : DjangoBook v1.0' % (label,),
            'news_list': News.objects.order_by('-datetime')[:5]}

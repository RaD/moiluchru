# -*- coding: utf-8 -*-

import django
#from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.http import Http404
from cargo import settings
from cargo.djangobook.models import News, Claims, ClaimStatus

import zipfile
from datetime import datetime, timedelta

news_info_extra = {
    'spelling_error_count': lambda: Claims.objects.count(),
    'django_version': django.get_version()
}

news_info = {
    'queryset': News.objects.order_by('-datetime')[:5],
    'template_name': 'news-list.html',
    'extra_context': news_info_extra # дополнительный контекст
}

def get_claims_count_by_status(code):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute ('select id from djangobook_claimstatus where status=%i and \
    applied in (select max(applied) from djangobook_claimstatus group by claim_id)' % int(code))
    return int(cursor.rowcount)

def show_db_page(request, chapter=None, section=None):
    """Show book's page."""
    if chapter == 'ap':
        page = 'ap%s.html' % section
    elif chapter is None and section is None:
        page = 'index.html'
    elif section is None:
        page = 'ch%s.html' % chapter
    else:
        page = 'ch%ss%s.html' % (chapter, section)
    # get the page from ZIP archive
    try:
        z = zipfile.ZipFile(settings.DJANGOBOOK_PAGE_ZIP)
        content = z.read(page)
	z.close()
    except (IOError, KeyError):
        raise TemplateDoesNotExist(template_name)
    
    return render_to_response('page.html',
                              {'page_title': 'DjangoBook v1.0',
                               'news_list': News.objects.order_by('-datetime')[:5],
                               'page_content': content,
                               'django_version': django.get_version(),
                               'user': request.user,
                               'debug': settings.DEBUG,
                               'spelling_error_count_pending': get_claims_count_by_status(1),
                               'spelling_error_count_assigned': get_claims_count_by_status(2),
                               'spelling_error_count_fixed': get_claims_count_by_status(3),
                               'spelling_error_count_invalid': get_claims_count_by_status(4),
                               'readers_count': len(request.session.get('readers', {}))})
    
def user_claims(request):
    """ This function handles users' claims on spelling error.
    It saves all information into Claims model. It doesn't check
    the fields' length. """
    if (request.is_ajax()):
        record = Claims(ctx_left=request.POST.get('ctx_left', ''),
                        selected=request.POST.get('selected', 'None'),
                        ctx_right=request.POST.get('ctx_right', ''),
                        email=request.POST.get('email', ''),
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
        return HttpResponse('<result><code>400</code><desc>it must be ajax call</desc></result>', mimetype="text/xml")

def show_news_page(request, news_id=None):
    """Show news' page."""
    return render_to_response('news.html',
                              {'page_title': 'Новости: DjangoBook v1.0',
                               'news_list': News.objects.order_by('-datetime'),
                               'news_curr': News.objects.get(id=news_id),
                               'django_version': django.get_version(),
                               'debug': settings.DEBUG})

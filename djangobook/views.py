# -*- coding: utf-8 -*-

import django
#from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.http import Http404
from cargo import settings
from cargo.djangobook.models import Claims, News

import zipfile
from datetime import datetime

news_info_extra = {
    'spelling_error_count': lambda: Claims.objects.count(),
    'django_version': django.get_version()
}

news_info = {
    'queryset': News.objects.order_by('-datetime')[:5],
    'template_name': 'news-list.html',
    'extra_context': news_info_extra # дополнительный контекст
}

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
    # get pending claims
    pending = Claims.objects.count();
    return render_to_response('page.html',
                              {'page_title': 'DjangoBook v1.0',
                               'news_list': News.objects.order_by('-datetime')[:5],
                               'page_content': content,
                               'django_version': django.get_version(),
                               'user': request.user,
                               'spelling_error_count': pending})
    
def user_claims(request):
    """ This function handles users' claims on spelling error.
    It saves all information into Claims model. It doesn't check
    the fields' length. """
    if (request.is_ajax()):
        record = Claims(ctx_left=request.POST.get('ctx_left', ''),
                        selected=request.POST.get('selected', 'None'),
                        ctx_right=request.POST.get('ctx_right', ''),
                        email=request.POST.get('email', ''),
                        comment=request.POST.get('comment', 'No comments...'),
                        url=request.META.get('HTTP_REFERER', ''),
                        datetime=datetime.now())
        record.save()
        return HttpResponse('<result>ok</result>', mimetype="text/xml")
    else:
        return HttpResponse('<result>error</result>', mimetype="text/xml")

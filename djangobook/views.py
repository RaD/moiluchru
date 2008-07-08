# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.http import Http404
from cargo import settings
from cargo.djangobook.models import Claims

import zipfile
from datetime import datetime

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
    except (IOError, KeyError):
        raise TemplateDoesNotExist(template_name)
    z.close()
    # get pending claims
    pending = Claims.objects.count();
    return render_to_response('djangobook_page.html',
                              {'page_content': content,
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
                        comment=request.POST.get('comment', 'No comments...'),
                        url=request.META.get('HTTP_REFERER', ''),
                        datetime=datetime.now())
        record.save()
        return HttpResponse('<result>ok</result>', mimetype="text/xml")
    else:
        return HttpResponse('<result>error</result>', mimetype="text/xml")

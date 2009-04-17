# -*- coding: utf-8 -*-
# http://markeev.labwr.ru/2008/07/django.html

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson

def render_to(template, processor):
    """ http://www.djangosnippets.org/snippets/821/

    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request, processors=[processor]))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request, processors=[processor]))
            return output
        return wrapper
    return renderer

def columns(param, count):
    def cols(func):
        def wrapper(request, *args, **kwargs):
            context =  func(request, *args, **kwargs)
            if param in context:
                object_list = context.get(param, None)
                length = len(object_list)
                per_page = length/count
                column_list = []
                for i in range(count):
                    column_list.append(object_list[i*per_page:(i+1)*per_page])
                context['column_list'] = column_list
            return context
        return wrapper
    return cols

def paginate_by(param_name, get_name, count=10):
    def paged(func):
        def wrapper(request, *args, **kwargs):
            try:
                pagenum = kwargs.get(get_name, '1')
                del(kwargs[get_name])
            except ValueError:
                pagenum = 1
            except KeyError:
                pass
            if pagenum is None:
                pagenum = 1
            # получаем контекст
            context =  func(request, *args, **kwargs)
            if param_name in context:
                objects = context.get(param_name)
                paginator = Paginator(objects, count)
                context['page'] = paginator.page(int(pagenum))
                context['page_range'] = paginator.page_range
                try:
                    context[param_name] = paginator.page(int(pagenum)).object_list
                except (EmptyPage, InvalidPage):
                    context[param_name] = paginator.page(paginator.num_pages).object_list
            return context
        return wrapper
    return paged

def ajax_processor(form_object):
    def processor(func):
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST':
                form = form_object(request.POST)
                if form.is_valid():
                    result = func(request, form, *args, **kwargs)
                else:
                    result = {'code': '301', 'desc': 'form is not valid'}
            else:
                result = {'code': '401', 'desc': 'it must be POST'}
            json = simplejson.dumps(result)
            return HttpResponse(json, mimetype="application/json")
        return wrapper
    return processor


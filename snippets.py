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

def ajax_processor(form_object=None):
    def processor(func):
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST':
                if form_object is not None:
                    form = form_object(request.POST)
                    if form.is_valid():
                        result = func(request, form, *args, **kwargs)
                    else:
                        result = {'code': '301', 'desc': 'form is not valid'}
                else:
                    result = func(request, *args, **kwargs)
            else:
                result = {'code': '401', 'desc': 'it must be POST'}
            json = simplejson.dumps(result)
            return HttpResponse(json, mimetype="application/json")
        return wrapper
    return processor

import os, Image
from django.conf import settings

THUMBNAILS = 'thumbnails'
SCALE_WIDTH = 'w'
SCALE_HEIGHT = 'h'
SCALE_BOTH = 'x'

def scale(max_x, pair):
    x, y = pair
    new_y = (float(max_x) / x) * y
    return (int(max_x), int(new_y))
    
# Thumbnail filter based on code from
# http://batiste.dosimple.ch/blog/2007-05-13-1/

def thumbnail(original_image_path, arg):
    if not original_image_path:  
        return ''  
        
    if arg.find(','):
        size, upload_path = [a.strip() for a in  arg.split(',')]
    else:
        size = arg
        upload_path = ''

    if (size.lower().endswith('h')):
        mode = SCALE_HEIGHT
    elif (size.lower().endswith('w')):
        mode = SCALE_WIDTH
    else:
        mode = SCALE_BOTH
        
    # defining the size  
    size = size[:-1]
    max_size = int(size.strip())
    
    # defining the filename and the miniature filename  
    basename, format = original_image_path.rsplit('.', 1)  
    basename, name = basename.rsplit(os.path.sep, 1)  

    miniature = name + '_' + str(max_size) + mode + '.' + format
    thumbnail_path = os.path.join(basename, THUMBNAILS)
    if not os.path.exists(thumbnail_path):  
        os.mkdir(thumbnail_path)  
    
    miniature_filename = os.path.join(thumbnail_path, miniature)  
    miniature_url = '/'.join((settings.MEDIA_URL, upload_path, THUMBNAILS, miniature))  
    
    # if the image wasn't already resized, resize it  
    if not os.path.exists(miniature_filename) \
        or os.path.getmtime(original_image_path) > os.path.getmtime(miniature_filename):
        image = Image.open(original_image_path)  
        image_x, image_y = image.size  

        if mode == SCALE_BOTH:
            if image_x > image_y:
                mode = SCALE_WIDTH
            else:
                mode = SCALE_HEIGHT
            
        if mode == SCALE_HEIGHT:
            image_y, image_x = scale(max_size, (image_y, image_x))
        else:
            image_x, image_y = scale(max_size, (image_x, image_y))
            
        
        image = image.resize((image_x, image_y), Image.ANTIALIAS)
              
        image.save(miniature_filename, image.format)

    return miniature_url  


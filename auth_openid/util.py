import re

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

def uri_to_username(uri):
    return re.sub('r[^0-9a-z]', '_', uri)


def render_to(template_path):
    """
    Decorate the django view.

    Wrap view that return dict of variables, that should be used for
    rendering the template.
    Dict returned from view could contain special keys:
     * MIME_TYPE: mimetype of response
     * TEMPLATE: template that should be used insted one that was
                 specified in decorator argument
    """

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            kwargs = {'context_instance': RequestContext(request)}
            if 'MIME_TYPE' in output:
                kwargs['mimetype'] = output.pop('MIME_TYPE')

            template = template_path
            if 'TEMPLATE' in output:
                template = output.pop('TEMPLATE')
            return render_to_response(template, output, **kwargs)
        return wrapper
    return decorator


def str_to_class(str):
    from django.db.models.loading import get_app
    mod_str, cls_str = str.rsplit('.', 1)
    mod = __import__(mod_str, globals(), locals(), ['foobar'])
    cls = getattr(mod, cls_str)
    return cls


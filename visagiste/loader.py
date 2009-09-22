# -*- coding: utf-8 -*-

from django.conf import settings
from django.template import TemplateDoesNotExist

from visagiste import models

def load_template_source(template_name, template_dirs=None):
    """ Loads templates from database. """
    tried = []
    for app in settings.INSTALLED_APPS:
        try:
            template = models.Template.objects.get(name=template_name)
            return (template.content, template_name)
        except models.Template.DoesNotExist:
            tried.append(template_name)
    if tried:
        error_msg = "Tried %s" % tried
    else:
        error_msg = "Your INSTALLED_APPS setting is empty. Check it."
    raise TemplateDoesNotExist, error_msg
load_template_source.is_usable = True

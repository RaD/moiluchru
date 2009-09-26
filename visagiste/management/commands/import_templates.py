# -*- coding: utf-8 -*-

# Команда manage.py для импортирования шаблонов в модель.

from django.conf import settings
from django.core.management.base import NoArgsCommand

from visagiste.models import Template

import os, glob

class Command(NoArgsCommand):
    help = "Populates Visagiste.Template model with the content of templates. Useful after installation."

    def handle_noargs(self, **options):
        Template.objects.all().delete()
        for indir in settings.TEMPLATE_DIRS:
            for infile in glob.glob(os.path.join(indir, '*.html')):
                content = open(infile, 'r').read()
                Template(name=infile, content=content).save()
                print infile

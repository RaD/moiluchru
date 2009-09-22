include config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)
SUBDIRS=advice css dumps jabber js locale manager pics shop \
	templates text visagiste
FILES=$(wildcard *.py) django.wsgi
LANGS=ru

all: locale subdirs

help:
	echo -en '\nUseful commands:\n\tinstall\n\tclean\n\ttranslate\n\tshow\n\tget\n\timport_db\n\timport_pics\n\n'

install: create_dir install_files install_subdirs chown_all
	mkdir -p $(CURRENT_INSTALL_DIR)/media/itempics/thumbnails
	chmod -R o+w $(CURRENT_INSTALL_DIR)/media/itempics/*

clean: clean_subdirs
	rm -f $(wildcard *.pyc) *~

locale: $(MO)

dump:
	grep PASS settings.py
	mysqldump -u moiluchru -p moiluchru > moiluchru.mysql.dump

translate:
	for i in $(LANGS); do \
		django-admin.py makemessages -l $$i; \
	done

%.mo: %.po
	django-admin.py compilemessages

agent:
	. ./ssh-agent.sh

show:
	ssh rad@caml.ru ls -l ~/django/moiluchru/dumps

get:
	scp rad@caml.ru:django/moiluchru/dumps/`date '+%Y%m%d'`.* ./dumps/

import_db:
	dbdump=`ls ./dumps/*bz2|sort|tail -1`; \
	impsql=`dirname $$dbdump`/`basename $$dbdump .dump.bz2`.sql; \
	echo $$dbdump; \
	bzcat $$dbdump > $$impsql; \
	echo "\. $$impsql"; \
	./manage.py dbshell

import_pics:
	picsdump=`pwd`/`ls ./dumps/*tar|sort|tail -1`; \
	cd $(CURRENT_INSTALL_DIR)/media/itempics/; \
	tar xvf $$picsdump

include targets.mk

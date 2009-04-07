include config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)
SUBDIRS=css js locale pics shop templates
FILES=$(wildcard *.py) django.wsgi
LANGS=ru

all: locale subdirs

install: create_dir install_files install_subdirs chown_all

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

pushhome:
	git push ssh://rad@nemo/~/development/git.repos/moiluchru.git/

pushprod:
	git push ssh://rad@caml.ru/~/sites/moiluchru/repos/moiluchru.git/

include targets.mk

include config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)
SUBDIRS=auth_openid css djangobook files js locale pics shop templates
FILES=$(wildcard *.py) django.wsgi
LANGS=ru

all: locale subdirs

install: create_dir install_files install_subdirs chown_all

clean: clean_subdirs
	rm -f $(wildcard *.pyc) *~

locale: $(MO)

dump:
	grep PASS settings.py
	mysqldump -u cargo -p cargo > cargo.mysql.dump

translate:
	for i in $(LANGS); do \
		django-admin.py makemessages -l $$i; \
	done

%.mo: %.po
	django-admin.py compilemessages

pushhome:
	git push ssh://rad@nemo/~/development/git.repos/cargo.git/

pushcargo:
	git push ssh://rad@caml.ru/~/sites/cargo/repos/cargo.git/

include targets.mk

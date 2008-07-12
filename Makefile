include config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)
SUBDIRS=css djangobook js locale pics shop templates
FILES=$(wildcard *.py)

all: locale subdirs

install: create_dir install_files install_subdirs chown_all

clean: clean_subdirs
	rm -f $(wildcard *.pyc) *~

locale: $(MO)

%.mo: %.po
	django-admin.py compilemessages

include targets.mk

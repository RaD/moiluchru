TOP_DIR=..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/djangobook
SUBDIRS=css js patches pics templates
FILES=$(wildcard *.py)

all:

install: create_dir install_files install_subdirs

clean:
	rm -f $(wildcard *.pyc) *~

include $(TOP_DIR)/targets.mk

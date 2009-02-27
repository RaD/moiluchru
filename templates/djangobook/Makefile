TOP_DIR=../..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/templates/djangobook
TEMPLATES=$(wildcard *.html)
SUBDIRS=feeds

all: 

install: create_dir install_templates install_subdirs

clean:
	rm -f *.zip *~

include $(TOP_DIR)/targets.mk

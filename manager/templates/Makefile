TOP_DIR=../..
APP_DIR=..

include $(TOP_DIR)/config.mk
include $(APP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/templates/$(APPNAME)
TEMPLATES=$(wildcard *.html)
SUBDIRS=

all: 

install: create_dir install_templates

clean:
	rm -f *.zip *~

include $(TOP_DIR)/targets.mk

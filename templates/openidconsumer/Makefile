TOP_DIR=../..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/templates/openidconsumer
TEMPLATES=$(wildcard *.html)

all:

install: create_dir install_templates

clean:
	rm -f *.mo *~

include $(TOP_DIR)/targets.mk

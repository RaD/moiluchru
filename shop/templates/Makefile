TOP_DIR=../..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/shop/templates
FILES=$(wildcard *.html)

all:

install: create_dir install_templates

clean:
	rm -f *.mo *~

include $(TOP_DIR)/targets.mk

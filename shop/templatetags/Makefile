TOP_DIR=../..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/shop/templatetags
FILES=$(wildcard *.py)

all:

install: create_dir install_templates

clean:
	rm -f $(wildcard *.pyc) *~

include $(TOP_DIR)/targets.mk

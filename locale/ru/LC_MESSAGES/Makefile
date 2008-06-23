TOP_DIR=../../..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/locale/ru/LC_MESSAGES
FILES=$(wildcard *.mo)

all:

install: create_dir install_files

clean:
	rm -f *.mo *~

include $(TOP_DIR)/targets.mk

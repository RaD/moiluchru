TOP_DIR=..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/dumps
FILES=$(wildcard *.sh)

all:

install: create_dir install_files

clean:
	rm -f *~

include $(TOP_DIR)/targets.mk

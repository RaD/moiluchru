TOP_DIR=../..
APP_DIR=..

include $(TOP_DIR)/config.mk
include $(APP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/$(APPNAME)/patches
FILES=$(wildcard *.sql)

all:

install: create_dir install_files

clean:
	rm -f *.mo *~

include $(TOP_DIR)/targets.mk

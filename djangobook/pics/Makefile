TOP_DIR=../..
APP_DIR=..

include $(TOP_DIR)/config.mk
include $(APP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_APACHE_DIR)/pics
FILES=$(wildcard *.png)

all:

install: create_dir install_files

clean:
	rm -f *~

include $(TOP_DIR)/targets.mk

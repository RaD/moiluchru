TOP_DIR=..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_APACHE_DIR)/js
FILES=$(wildcard *.js)

all:

install: create_dir install_files

clean:
	rm -f $(wildcard *.pyc) *~

include $(TOP_DIR)/targets.mk

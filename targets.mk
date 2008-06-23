#
# Действия
# $Id$
#

MAKE=`which make`

subdirs:
	for i in $(SUBDIRS) end-of-subdirs-list; do \
		if [ $$i != end-of-subdirs-list ]; then \
			cd $$i; $(MAKE); cd -; \
		fi; \
	done

install_subdirs:
	for i in $(SUBDIRS) end-of-subdirs-list; do \
		if [ $$i != end-of-subdirs-list ]; then \
			cd $$i; $(MAKE) install; cd -; \
		fi; \
	done

clean_subdirs:
	for i in $(SUBDIRS) end-of-subdirs-list; do \
		if [ $$i != end-of-subdirs-list ]; then \
			cd $$i; $(MAKE) clean; cd -; \
		fi; \
	done

create_dir:
	mkdir -p $(CURRENT_INSTALL_DIR);

install_files:
	cp $(FILES) $(CURRENT_INSTALL_DIR)/;

chown_all:
	chown -R $(OWNER):$(GROUP) $(CURRENT_INSTALL_DIR);


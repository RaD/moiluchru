TOP_DIR=../..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/djangobook/templates
DJZIP=djangobook.html.zip
FILES=$(wildcard *.html) $(DJZIP)

all: 

zip: $(DJZIP)

sendzip: $(DJZIP)
	scp $(DJZIP) caml.ru:devel/djangobook.git/templates/
	echo "Go to the site and make install"

$(DJZIP): $(HTMLS_SRC)/*.html
	set -x;
	mkdir ./zip;
	for i in `ls $(HTMLS_SRC)/*.html`; do \
	    echo `basename $$i`; \
	    cat $$i | \
	    sed 's/^.*<body[^>]*>//' | \
	    sed 's/<\/body>.*$$//' \
	    > ./zip/`basename $$i`; \
	done;
	cd ./zip; \
	zip -m ../$(DJZIP) *.html; \
	cd -; \
	rmdir ./zip; \

install: create_dir install_templates

clean:
	rm -f *.zip *~

include $(TOP_DIR)/targets.mk

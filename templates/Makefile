HTMLS=/home/rad/docbookxml/HTML/djangobook

all:
	set -x;
	for i in `ls $(HTMLS)/*.html`; do \
	    echo `basename $$i`; \
	    cat $$i | \
	    sed 's/^.*<body[^>]*>//' | \
	    sed 's/<\/body>.*$$//' \
	    > ./zip/`basename $$i`; \
	done;
	cd ./zip; \
	zip -m djangobook.html.zip *.html; \
	mv djangobook.html.zip ../;

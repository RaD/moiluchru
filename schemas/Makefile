DOT=$(wildcard *.dot)
PNG=$(patsubst %.dot,%.png,$(DOT))

all: $(PNG)

clean: $(PNG)
	rm -rf *.png *~

# пример использования временного файла для изменения кодировки
#%.utf: %.dot
#	iconv -t utf-8 $< > $*.utf

%.png: %.dot
	dot -Tpng $< > $@

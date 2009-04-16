#!/bin/bash

BASE=~/django/moiluchru
DIR=$BASE/dumps
PIC=$BASE/media/itempics
DF=$DIR/`date '+%Y%m%d'`.pics.tar

cd $PIC
tar cf $DF `find . -type f`
cd -
find $DIR -name '*.pics.tar' -mtime +6 -delete
exit 0

#!/bin/bash

BASE=~/django/moiluchru
DIR=$BASE/dumps
PIC=$BASE/media/itempics
DF=$DIR/`date '+%Y%m%d'`.pics.bz2

cd $PIC
tar cjf $DF `find . -type f`
cd -
exit 0

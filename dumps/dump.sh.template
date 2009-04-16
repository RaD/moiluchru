#!/bin/bash

DIR=~/django/moiluchru/dumps
DF=$DIR/`date '+%Y%m%d'`.dump

mysqldump -u moiluchru --password='q1' moiluchru > $DF
bzip2 $DF
find $DIR -name '*.dump.bz2' -mtime +6 -delete
exit 0

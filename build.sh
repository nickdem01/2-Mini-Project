#!/bin/bash

sort -u -o recs.txt recs.txt

sort -u -o dates.txt dates.txt

perl break.pl < dates.txt > datestemp.txt

db_load -c duplicates=1 -T -f datestemp.txt -t btree da.idx

perl break.pl < recs.txt > recstemp.txt

db_load -c duplicates=1 -T -f recstemp.txt -t btree re.idx

rm datestemp.txt recstemp.txt 
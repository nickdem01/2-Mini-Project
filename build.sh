#!/bin/bash

sort -u -o recs.txt recs.txt

sort -u -o dates.txt dates.txt

sort -u -o emails.txt emails.txt

sort -u -o terms.txt terms.txt

perl break.pl < dates.txt > datestemp.txt

db_load -c duplicates=1 -T -f datestemp.txt -t btree da.idx

perl break.pl < emails.txt > emailstemp.txt

db_load -c duplicates=1 -T -f emailstemp.txt -t btree em.idx

perl break.pl < terms.txt > termstemp.txt

db_load -c duplicates=1 -T -f termstemp.txt -t btree te.idx

perl break.pl < recs.txt > recstemp.txt

db_load -c duplicates=1 -T -f recstemp.txt -t hash re.idx

rm datestemp.txt recstemp.txt emailstemp.txt termstemp.txt

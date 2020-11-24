#!/bin/bash
cut -f 1 beers.txt | sort | uniq -c | sort -k 1 -t$'\t' -nr | head

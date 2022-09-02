#!/bin/bash

#usage: merge_subs.sh [sub_file...] out_file 

OUT=${@: -1}
INP=${@:1:$#-1}


cat $INP \
| grep -iv "WEBVTT" \
| grep -iv "Kind: captions" \
| grep -iv "Language: " \
| grep -v '\-\->' \
| grep -iv '<c>' \
| grep -v "^\s*$" \
| uniq \
> $OUT

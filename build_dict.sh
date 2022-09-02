#!/bin/bash

source scripts/common.sh

for lang in $(ls data)
do 
    lang_dir=data/$lang
    colored yellow processing $lang

    colored blue "cleaning subtitle files"
    ./scripts/merge_subs.sh $lang_dir/subs/* $lang_dir/merged.txt

    colored blue "building dictionary"
    python scripts/build_dictionary.py $lang_dir/merged.txt -l $lang -o $lang_dir/dict.tsv
done

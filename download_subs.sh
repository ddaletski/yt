#!/bin/bash

DIR=$1

LIST=$DIR/videos_list

OUT=$DIR/subs

cat $LIST | parallel -n1 -j8 "youtube-dl  --all-subs --skip-download -o '$OUT/subs/%(id)s.%(ext)s' 'https://www.youtube.com/watch?v={}'"

#!/bin/bash

LIST=$1 # videos list
OUT_DIR=$2 # subtitles dir
LNG=$3 # subs language

cat $LIST | parallel -n1 "yt-dlp \
--write-sub --write-auto-sub --sub-lang=${LNG} --skip-download \
-o '$OUT_DIR/%(id)s.%(ext)s' \
'https://www.youtube.com/watch?v={}'"

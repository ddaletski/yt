#!/bin/bash
OUT=$1
PLAYLIST="${@:2}"
echo $PLAYLIST

mkdir -p $OUT
youtube-dl --get-id $PLAYLIST > $OUT/videos_list

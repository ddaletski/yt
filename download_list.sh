#!/bin/bash

OUT=$1 # output dir to download videos_list
PLAYLIST="${@:2}"

#---------------------------------#

mkdir -p $OUT
youtube-dlc --get-id $PLAYLIST > $OUT/videos_list

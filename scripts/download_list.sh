#!/bin/bash

PLAYLIST=$1
#---------------------------------#

yt-dlp --get-id $PLAYLIST --max-downloads 30

#!/bin/bash

PLAYLIST=$1
#---------------------------------#

youtube-dlc --get-id $PLAYLIST >> videos_list

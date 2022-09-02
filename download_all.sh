#!/bin/bash

source scripts/common.sh

for lang in $(ls channels | parallel -n1 echo {/.})
do 
    lang_dir=data/$lang
    rm -f $lang_dir/videos_list.txt

    colored blue "downloading videos list from channels"
    for channel in $(cat channels/$lang.tsv)
    do 
        colored purple $channel
        ./scripts/download_list.sh $channel >> $lang_dir/videos_list.txt
    done

    colored blue "downloading videos subtitles"
    ./scripts/download_subs.sh $lang_dir/videos_list.txt $lang_dir/subs $lang
done

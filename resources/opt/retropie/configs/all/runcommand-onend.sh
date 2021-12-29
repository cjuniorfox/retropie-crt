#!/bin/sh
timing=$(cat ../../../../boot/config.txt | grep hdmi_timings | sed 's/ngs=/ngs /g')
echo $timing
#tvservice -e "CEA 7" ; sleep 3 ; fbset -depth 8 ; fbset -depth 32; tvservice -s

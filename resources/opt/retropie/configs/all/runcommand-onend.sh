#!/bin/sh
timing=$(cat ../../../../boot/config.txt | grep hdmi_timings | sed 's/ngs=/ngs /g')
vcgencmd "${timing}" && \
	tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && \
	fbset -depth 32 2&1 > /dev/null
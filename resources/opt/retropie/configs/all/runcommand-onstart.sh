#!/bin/sh
#tvservice -e "DMT 87"
#sleep 3
#fbset -depth 8
#fbset -depth 32
#tvservice -s

#!/bin/bash
#
# Useful data are passed as arguments to these scripts:
#
# $1 - the system (eg: atari2600, nes, snes, megadrive, fba, etc).
# $2 - the emulator (eg: lr-stella, lr-fceumm, lr-picodrive, pifba, etc).
# $3 - the full path to the rom file.
# $4 - the full command line used to launch the emulator.
#

#<h_active_pixels> = horizontal pixels (width)
#<h_sync_polarity> = invert hsync polarity
#<h_front_porch>   = horizontal forward padding from DE acitve edge
#<h_sync_pulse>    = hsync pulse width in pixel clocks
#<h_back_porch>    = vertical back padding from DE active edge
#<v_active_lines>  = vertical pixels height (lines)
#<v_sync_polarity> = invert vsync polarity
#<v_front_porch>   = vertical forward padding from DE active edge
#<v_sync_pulse>    = vsync pulse width in pixel clocks
#<v_back_porch>    = vertical back padding from DE active edge
#<v_sync_offset_a> = leave at zero
#<v_sync_offset_b> = leave at zero
#<pixel_rep>       = leave at zero
#<frame_rate>      = screen refresh rate in Hz
#<interlaced>      = leave at zero
#<pixel_freq>      = clock frequency (width*height*framerate)
#<aspect_ratio>    = *

systemName="$1"
emuName="$2"

consoledisp "${systemName}" 2&1 > /dev/null
exit 0;
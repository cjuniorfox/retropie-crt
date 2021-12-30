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

pal_mastersystem(){
	vcgencmd hdmi_timings 1136 1 35 101 120 288 0 2 2 19 0 0 4 50.000 0 21400000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 284 -yres 288 -depth 32
}
ntsc_gamegear(){
	vcgencmd hdmi_timings 1392 0 41 124 124 240 0 2 2 17 0 0 4 58.920 0 25900000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 348 -yres 240 -depth 32
}
ntsc_megadrive(){
	vcgencmd hdmi_timings 1280 0 105 125 189 240 0 2 2 17 0 0 1 59.920 0 26700000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 1280 -yres 240 -depth 32
}
ntsc_mastersystem(){
	vcgencmd hdmi_timings 1136 0 33 101 101 240 0 2 2 17 0 0 4 59.920 0 21500000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 284 -yres 240 -depth 32
}
ntsc_tms9918(){
	vcgencmd hdmi_timings 1024 0 89 101 157 192 0 26 26 17 0 0 4 59.920 0 21500000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 256 -yres 192 -depth 32
}
ntsc_neogeo(){
	vcgencmd hdmi_timings 1392 0 41 124 124 240 0 2 2 17 0 0 4 59.185 0 26100000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 348 -yres 240 -depth 32
}
ntsc_nes(){
	vcgencmd hdmi_timings 1024 0 72 98 138 240 0 2 2 17 0 0 4 60.100 0 21000000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 256 -yres 240 -depth 32
}
ntsc_snes(){
	vcgencmd hdmi_timings 1024 0 72 98 138 240 0 2 2 17 0 0 2 60.100 0 21000000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 512 -yres 240 -depth 32
}
ntsc_pcengine(){
	vcgencmd hdmi_timings 1024 0 72 98 138 224 0 10 10 17 0 0 4 59.940 0 20900000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 256 -yres 224 -depth 32
}
ntsc_arcade(){
	vcgencmd hdmi_timings 1920 0 82 175 200 240 0 2 2 17 0 0 1 59.940 0 37300000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 1920 -yres 240 -depth 32
}

case "$systemName" in

	"megadrive") # Load Sega Megadrive timings
		ntsc_megadrive;;
	"genesis") # Load Sega Genesis timings
		ntsc_megadrive;;
	"sega32x") # Load Sega 32X timings
		ntsc_megadrive;;
	"segacd") # Load Sega CD timings
		ntsc_megadrive;;
	"mastersystem") # Load Sega Master System timings
		ntsc_mastersystem;;
	"gamegear") # Load Sega Game Gear timings
		ntsc_mastersystem;;

"atarilynx") # Load Atari Lynx timings
vcgencmd hdmi_timings 1920 1 48 192 240 240 1 3 3 16 0 0 0 59.92 0 37680000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 240
;;
	"neogeo") # Load SNK Neo Geo timings
		ntsc_neogeo;;

	"pcengine") # Load NEC PC Engine timings
		ntsc_pcengine;;

	"supergrafx") # Load NEC PC Engine timings
		ntsc_pcengine;;
	"nes") # Load NES timings
		ntsc_nes;;
	"fds") # Load FDS timings
		ntsc_nes;;
	"snes") # Load SNES timings
		ntsc_snes;;
	"msx") # Load MSX timings
		ntsc_tms9918;;

"psx") # Load PSX timings
vcgencmd hdmi_timings 1920 1 48 192 240 248 1 3 10 6 0 0 0 60 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 240
;;

"gb") # Load Game Boy timings
vcgencmd hdmi_timings 1920 1 48 192 280 288 1 3 10 6 0 0 0 59.73 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 288
;;

"gbc") # Load Game Boy Color timings
vcgencmd hdmi_timings 1920 1 48 192 280 288 1 3 10 6 0 0 0 59.73 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 288
;;

"gba") # Load Game Boy Advance timings
vcgencmd hdmi_timings 1920 1 48 192 300 320 1 3 10 6 0 0 0 59.73 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 320
;;

"ngp") # Load SNK Neo Geo Pocket timings
vcgencmd hdmi_timings 1920 1 160 200 228 228 1 9 8 21 0 0 0 60 0 40410000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 228
;;

"ngpc") # Load SNK Neo Geo Pocket Color timings
vcgencmd hdmi_timings 1920 1 160 200 228 228 1 9 8 21 0 0 0 60 0 40410000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 228
;;

"atari2600") # Load Atari 2600 timings
vcgencmd hdmi_timings 1920 1 48 192 200 248 1 3 10 6 0 0 0 59.92 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 200
;;

"atari5200") # Load Atari 5200 timings
vcgencmd hdmi_timings 1920 1 48 192 240 248 1 3 10 6 0 0 0 59.92 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 240
;;

"atari7800") # Load Atari 7800 timings
vcgencmd hdmi_timings 1920 1 48 192 240 248 1 3 10 6 0 0 0 59.92 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 240
;;

"wonderswan") # Load Bandai Wonderswan timings
vcgencmd hdmi_timings 1920 1 48 192 280 288 1 3 10 6 0 0 0 59.73 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 288
;;

"wonderswancolor") # Load Bandai Wonderswan Color timings
vcgencmd hdmi_timings 1920 1 48 192 280 288 1 3 10 6 0 0 0 59.73 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 288
;;

"virtualboy") # Load Virtual Boy timings
vcgencmd hdmi_timings 1920 1 160 200 286 224 1 9 8 21 0 0 0 60.10 0 40410000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 224
;;

	"mame-libretro") # Load MAME Generic 320x240 timings
		ntsc_arcade;;

	"fba") # Load FBAlpha Generic 320x240 timings
		ntsc_arcade;;

	"arcade") # Load Arcade Generic 320x240 timings
		if [ "$emuName" != "advmame" ]; then
			ntsc_arcade
		fi;;

"n64") # Load Nintendo 64 timings
vcgencmd hdmi_timings=320 1 15 29 40 240 1 10 14 16 0 0 0 60 0 6400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 320 -yres 240
;;

"doom") # Generic 320x240 timings
vcgencmd hdmi_timings 1920 1 48 192 240 248 1 3 10 6 0 0 0 60 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 240
;;

"quake") # Generic 320x240 timings
vcgencmd hdmi_timings 1920 1 48 192 240 248 1 3 10 6 0 0 0 60 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 240
;;

"pc") # Load Generic DOS 320x240 timings
vcgencmd hdmi_timings 1920 1 48 192 240 248 1 3 10 6 0 0 0 60 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 240
;;
esac

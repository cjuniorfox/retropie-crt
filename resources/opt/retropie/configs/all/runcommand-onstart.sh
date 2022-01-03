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

if - "${systemName}" = "x68000" ]; then
	consoledisp "${systemName}" --pal
else
	consoledisp "${systemName}"
fi;
exit 0;

pal_mastersystem(){
	vcgencmd hdmi_timings 1136 1 35 101 120 288 0 2 2 19 0 0 4 50.000 0 21400000 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 284 -yres 288 -depth 32
}

ntsc_atarilynx(){
	vcgencmd hdmi_timings 1044 0 31 94 94 240 0 3 2 17 0 0 3 59.940 0 19806254 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 348 -yres 240 -depth 32
}

ntsc_megadrive(){
	chvideo -f 59.92 -p -w 1392
}
ntsc_mastersystem(){
	vcgencmd hdmi_timings 1136 0 33 102 102 240 0 3 2 17 0 0 4 59.920 0 21546673 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 284 -yres 240 -depth 32
}
ntsc_tms9918(){
	vcgencmd hdmi_timings 1024 0 89 102 158 192 0 27 26 17 0 0 4 59.920 0 21546673 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 256 -yres 192 -depth 32
}
ntsc_neogeo(){
	vcgencmd hdmi_timings 1392 0 41 125 125 240 0 3 2 17 0 0 4 59.185 0 26086065 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 348 -yres 240 -depth 32
}
ntsc_nes(){
	vcgencmd hdmi_timings 1024 0 72 99 139 240 0 3 2 17 0 0 4 60.100 0 21011521 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 256 -yres 240 -depth 32
}
ntsc_snes(){
	vcgencmd hdmi_timings 1084 0 32 97 97 240 0 3 2 17 0 0 2 60.100 0 20632651 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 542 -yres 240 -depth 32
}
ntsc_pcengine(){
	vcgencmd hdmi_timings 1024 0 72 99 139 224 0 11 10 17 0 0 4 59.940 0 20955584 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 256 -yres 224 -depth 32
}
ntsc_arcade(){
	vcgencmd hdmi_timings 1920 0 82 176 201 240 0 3 2 17 0 0 1 59.940 0 37376826 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 1920 -yres 240 -depth 32
}

ntsc_gameboy(){
	vcgencmd hdmi_timings 1280 0 38 115 115 240 0 3 2 17 0 0 4 59.730 0 24208251 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 320 -yres 240 -depth 32
}

ntsc_atari2600(){
	vcgencmd hdmi_timings 1392 0 41 125 125 250 0 1 2 9 0 0 4 59.920 0 26410020 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 348 -yres 250 -depth 32
}
ntsc_atari5200(){
	vcgencmd hdmi_timings 1408 0 41 126 126 250 0 1 2 9 0 0 4 59.920 0 26709061 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 352 -yres 250 -depth 32
}
ntsc_atari7800(){
	vcgencmd hdmi_timings 1392 0 41 125 125 240 0 3 2 17 0 0 4 59.920 0 26410020 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 348 -yres 240 -depth 32
}
ntsc_neogeopocket(){
	vcgencmd hdmi_timings 1024 0 30 92 92 240 0 3 2 17 0 0 4 60.000 0 19447840 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 256 -yres 240 -depth 32
}
ntsc_nintendo64(){
	vcgencmd hdmi_timings 1392 0 41 125 125 240 0 3 2 17 0 0 2 60.000 0 26445280 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 696 -yres 240 -depth 32
}
ntsc_x68000(){
	vcgencmd hdmi_timings 1084 0 32 97 97 256 0 1 2 3 0 0 2 59.940 0 20577722 1 && tvservice -e DMT\ 88 && tvservice -e DMT\ 87 && sleep 0.5 && fbset -xres 542 -yres 256 -depth 32
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
		ntsc_atarilynx;;
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
	"x68000") # Load MSX timings
		ntsc_x68000;;

"psx") # Load PSX timings
vcgencmd hdmi_timings 1920 1 48 192 240 248 1 3 10 6 0 0 0 60 0 38400000 1
tvservice -e "DMT 87"
fbset -depth 32 && fbset -depth 32 -xres 1920 -yres 240
;;

	"gb") # Load Game Boy timings
		ntsc_gameboy;;
	"gbc") # Load Game Boy Color timings
		ntsc_gameboy;;
	"gba") # Load Game Boy Advance timings
		ntsc_gameboy;;

	"ngp") # Load SNK Neo Geo Pocket timings
		ntsc_neogeopocket;;
	"ngpc") # Load SNK Neo Geo Pocket Color timings
		ntsc_neogeopocket;;

	"atari2600") # Load Atari 2600 timings
		ntsc_atari2600;;

	"atari5200") # Load Atari 5200 timings
		ntsc_atari5200;;

	"atari7800") # Load Atari 7800 timings
		ntsc_atari7800;;
	"mame-libretro") # Load MAME Generic 320x240 timings
		ntsc_arcade;;

	"fba") # Load FBAlpha Generic 320x240 timings
		ntsc_arcade;;

	"arcade") # Load Arcade Generic 320x240 timings
		if [ "$emuName" != "advmame" ]; then
			ntsc_arcade
		fi;;
	"n64") # Load Nintendo 64 timings
	#Warning: To works correctly, Its needed to install lr-mupen64
		ntsc_nintendo64;;

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

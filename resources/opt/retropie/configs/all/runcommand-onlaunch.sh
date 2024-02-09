#!/bin/bash
#
# Useful data are passed as arguments to these scripts:
#
# $1 - the system (eg: atari2600, nes, snes, megadrive, fba, etc).
# $2 - the emulator (eg: lr-stella, lr-fceumm, lr-picodrive, pifba, etc).
# $3 - the full path to the rom file.
# $4 - the full command line used to launch the emulator.
#


systemName="$1"
emuName="$2"
command="$4"
if [[ "${systemName}" == "mame-libretro" ]]; then
        chvideocore "${command}"
else    
        consoledisp "${systemName}" 2>&1> /dev/null
fi

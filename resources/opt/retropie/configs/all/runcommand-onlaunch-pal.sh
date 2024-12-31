#!/bin/bash
#
# Useful data are passed as arguments to these scripts:
#
# $1 - the system (eg: atari2600, nes, snes, megadrive, fba, etc).
# $2 - the emulator (eg: lr-stella, lr-fceumm, lr-picodrive, pifba, etc).
# $3 - the full path to the rom file.
# $4 - the full command line used to launch the emulator.
#

system_name="$1"
emu_name="$2"
rom_file="$3"
command="$4"
if [[ "${system_name}" == "mame-libretro" ]]; then
    chvideocore --command "${command}" --rom-file "${rom_file}"
else
    consoledisp "${system_name}" --pal
fi
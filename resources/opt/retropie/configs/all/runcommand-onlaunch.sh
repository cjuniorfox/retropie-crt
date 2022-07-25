#!/bin/bash
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

psx_dialog(){

    OPTIONS=(1 "Standard Progressive (240p)"
             2 "Hi-Res Interlaced (480i)")
    CHOICE=$(dialog \
                    --title "PSX Launcher" \
                    --menu "Choose the desired resolution" \
                    15 75 2 \
                    "${OPTIONS[@]}" \
                    2>&1 >/dev/tty)
    clear
    case $CHOICE in
            1)
                consoledisp psx 2>&1
                ;;
            2)
                consoledisp psx_i 2>&1
                ;;
    esac
}


systemName="$1"
emuName="$2"
consoledisp "${systemName}" 2>&1> /dev/null
#
#if [[ "${systemName}" = "psx" ]]; then
#    psx_dialog
#else
#    consoledisp "${systemName}" 2>&1
#fi;
#*
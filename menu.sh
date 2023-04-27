#!/bin/bash

# check, if sudo is used
if [[ "$(id -u)" -ne 0 ]]; then
    echo "Script must be run under sudo from the user you want to install for. Try 'sudo $0'"
    exit 1
fi

cd ~/retropie-crt
git pull

HEIGHT=15
WIDTH=75
CHOICE_HEIGHT=4
BACKTITLE="github.com/cjuniorfox/retropie-crt - RetroPie CRT."
TITLE="RetroPie CRT Setup Script"
MENU="Version: 0.0.2 - Developed by Carlos Junior <cjuniorfox@gmail.com>"
BACKTITLE="github.com/cjuniorfox/retropie-crt - RetroPie CRT."

dialog_msg(){
    MSGBOX="You're just about to set up the Raspberry's HDMI output to work accordingly with $1 - $2 settings.\n\
Be aware that maybe the Raspberry cannot be properly displayed on your High Definition TV using HDMI cable while the $1 mode is set.\n\n\
I also would like to remind you that you should have the bare cheap Chinese HDMI to YPbPr converter bought at Aliexpress or Banggood to make your Pi for getting work on your CRT Display.\n\n\
If you still have some doubts, ask questions at the official Github repository. if you have no doubts, feel free and go ahead."
}

success(){
    MSG="Good news! Feels like all the needed configuration has been finished with success!\n\
Enjoy the marvellous nostalgic good games through the scanlines from the cathode ray tube.\n\
It's a good idea to switch off your Raspberry Pi before connecting them to your CRT display.\n\n\
Would you like to turn it off now?"
    dialog --clear \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --yesno "$MSG" \
        $HEIGHT $WIDTH && sudo reboot || menu
}

log_stderr(){
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --colors \
        --textbox "stderr.log" \
        20 100 && menu
}

log_stdout(){
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --colors \
        --textbox "stdout.log" \
        20 100 && success
}

failed(){
    MSG="It's bad to be the bearer of such bad news, but something went wrong with the process.\n \
Could you take a look at the execution log to see what step the whole thing went wrong? \n\
If you believe the cause of the fail it's somehow related to some bug, feel free to open an issue on the project's Github page. \nSorry about that!\n\n\
Would you like to take a look at the log file?"
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --colors \
        --yesno "\Z1 $MSG" \
        $HEIGHT $WIDTH && log_stderr
}

end_dialog(){
    MSG="Hey dude! The installation process has finished with no issue at all. Would you like to look at the execution log file?"
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --colors \
        --yesno "$MSG" \
        $HEIGHT $WIDTH && log_stdout || success
}

ntsc(){
    dialog --infobox "Installing, please wait." 3 35
    python3 ./configure.py > >(tee stdout.log) 2> >(tee stderr.log >&2) && end_dialog || failed
}

pal(){
    dialog --infobox "Installing, please wait." 3 35
    python3 ./configure.py --pal > >(tee stdout.log) 2> >(tee stderr.log >&2) && end_dialog || failed
}

hdtv(){
    dialog --infobox "Installing, please wait." 3 35
    python3 ./configure.py -u > >(tee stdout.log) 2> >(tee stderr.log >&2) && end_dialog || failed
}

pal_confirm(){
    dialog_msg "B/D/G/H/I/K/N 625 50hz (PAL-EU/SECAM)" "[288p/576i@50.01Hz]"
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --yesno "$MSGBOX" \
        $HEIGHT $WIDTH && pal || menu
}

ntsc_confirm(){
    dialog_msg "System M 525 60Hz (PAL-M/NTSC)" "[240p/480i@59.975Hz]"
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --yesno "$MSGBOX" \
        $HEIGHT $WIDTH && ntsc || menu
}
hdtv_confirm(){
    msg="I'm about to change the HDMI output settings back to default.\n\n
\Z1Be aware that unless your CRT display should handle HDTV modes, keeping it connected while the HDTV mode it's on can harm the deflection yoke circuitry of the CRT display.\Zn\n\n
Are you sure?"
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --colors \
        --yesno "$msg" \
        $HEIGHT $WIDTH && hdtv || menu
}
menu(){

    OPTIONS=(1 "SDTV - 525 60Hz aka NTSC (Americas/Japan)"
             2 "SDTV - 625 50Hz aka PAL (Europe/Asia/Africa)"
             3 "HDTV (Default)")
    CHOICE=$(dialog \
                    --backtitle "$BACKTITLE" \
                    --title "$TITLE" \
                    --menu "$MENU" \
                    $HEIGHT $WIDTH $CHOICE_HEIGHT \
                    "${OPTIONS[@]}" \
                    2>&1 >/dev/tty)
    clear
    case $CHOICE in
            1)
                ntsc_confirm
                ;;
            2)
                pal_confirm
                ;;
            3)
                hdtv_confirm
                ;;
    esac
}

#git --help > /dev/null 2>&1 && dialog --help > /dev/null 2>&1 || echo apt update && apt install git dialog -y 
menu
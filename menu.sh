#!/bin/bash

# check, if sudo is used
if [[ "$(id -u)" -ne 0 ]]; then
    echo "Script must be run under sudo from the user you want to install for. Try 'sudo $0'"
    exit 1
fi

HEIGHT=15
WIDTH=75
CHOICE_HEIGHT=4
BACKTITLE="github.com/cjuniorfox/retropie-crt - RetroPie CRT."
TITLE="RetroPie CRT Setup Script"
MENU="Version: 0.0.1 - Developed by Carlos Junior <cjuniorfox@gmail.com>"
BACKTITLE="github.com/cjuniorfox/retropie-crt - RetroPie CRT."

dialog_msg(){
    MSGBOX="You're about to configure the Raspberry's HDMI output to work accordingly with $1 - $2 settings.\n\
Be aware it's maybe the Raspberry cannot be properly displayed at your HDTV using HDMI cable while the $1 mode is set.\n\n\
I also would like to remind you that you should have in hands the bare cheap chinese HDMI to YPbPr converter buyed at Aliexpress or Banggood to run on your CRT Display.\n\n\
If you sure about all, go ahead."
}

success(){
    MSG="Good news! Feels like all the needed configuration has been finished with success!\n\
Enjoy the marvelous nostalgic good games through the scanlines from the cathode ray tube.\n\
It's a good idea shut down your Raspberry Pi and connect them to your CRT. My mission ends here.\n\n\
Would you like to shutdown now?"
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
    MSG="I don't like being bearer of such bad news, but had something wrong with the process.\n \
Could you take a look the execution log to see what step had did wrong? \n\
Feel free to open an issue at projects Github page.\nSorry about that!\n\n\
Would you like to take a look at the log file?"
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --colors \
        --yesno "\Z1 $MSG" \
        $HEIGHT $WIDTH && log_stderr
}

end_dialog(){
    MSG="Hey dude! The installation proccess has finished with no issue reported. Would you like to look the execution's log file?"
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --colors \
        --yesno "$MSG" \
        $HEIGHT $WIDTH && log_stdout || success
}

ntsc(){
    python3 ./configure.py > >(tee stdout.log) 2> >(tee stderr.log >&2) && end_dialog || failed
}

pal(){
    python3 ./configure.py --pal > >(tee stdout.log) 2> >(tee stderr.log >&2) && end_dialog || failed
}

hdtv(){
    python3 ./configure.py -u > >(tee stdout.log) 2> >(tee stderr.log >&2) && end_dialog || failed
}

pal_confirm(){
    dialog_msg "PAL-EU" "[288p/625i@50.01Hz]"
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --yesno "$MSGBOX" \
        $HEIGHT $WIDTH && pal || menu
}

ntsc_confirm(){
    dialog_msg "NTSC/PAL-M" "[240p/480i@59.975Hz]"
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --yesno "$MSGBOX" \
        $HEIGHT $WIDTH && ntsc || menu
}
hdtv_confirm(){
    msg="You're about to fade back your Raspberry to work like another regular device that outputs HDTV signal over HDMI.\n
The scripts itself will not be uninstalled from this device, only the settings made.\n\n
\Z1Be aware that keeping the Raspberry conected to the CRT display while HDTV mode is set can \Zbdamage\Zn\Z1 the CRT's deflection circuitry.\Zn\n\n
If you sure, go ahead."
    dialog \
        --backtitle "$BACKTITLE" \
        --title "$TITLE" \
        --colors \
        --yesno "$msg" \
        $HEIGHT $WIDTH && hdtv || menu
}
menu(){

    OPTIONS=(1 "SDTV - NTSC/PAL-M (Americas/Japan)"
             2 "SDTV - PAL-EU (Europe/Africa)"
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
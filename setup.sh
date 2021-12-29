#!/bin/sh
#Only sudoers can do that
#if [ "$EUID" -ne 0 ]
#  then echo "Please run as root"
#  exit
#fi

#Install the boot
config=resources/boot/config.txt

#cat /boot/config.txt | grep -v 'overscan_scale\|hdmi_timings\|hdmi_group\|hdmi_mode' > /boot/config.txt
#cat "${config}" >> /boot/config.txt

#now the remaining scripts
runcommand_scripts="resources/opt/retropie/configs"

#cp "${runcommand_scripts}"/all/runcommand-*/sh /opt/retropie/configs/all

for f in "${runcommand_scripts}"/* ; do
    if [ -d "$f" ]; then
        platform=$(echo $f | sed "s|${runcommand_scripts}||g");
        conffile=${runcommand_scripts}${platform}/retroarch_crt.cfg
        if [ -f "$conffile" ]; then
            parameters="$( cat ${conffile} | awk '{ print $1 }')"
            filename="/opt/retropie/configs${platform}/retroarch.cfg";
            file="$(cat ${filename})"
            for  p in ${parameters} ; do
                file=$(echo"${file}" | grep "${p}")
            done;
            cat "${runcommand_scripts}${platform}/retroarch_crt.cfg" # > "${filename}"
            #echo "${file}" >> "${filename}"
        fi
    fi
done

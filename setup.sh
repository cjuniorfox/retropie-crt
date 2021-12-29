#!/bin/sh
#Only sudoers can do that
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

#Install the boot
config=resources/boot/config.txt

cat /boot/config.txt | grep -v 'overscan_scale\|hdmi_timings\|hdmi_group\|hdmi_mode' > /boot/config.txt
cat "${config}" >> /boot/config.txt

#now the remaining scripts
runcommand_scripts = "resources/opt/retropie/configs"

cp "${runcommand_scripts}"/all/runcommand-*/sh /opt/retropie/configs/all

for [ platform in {neogeo|nes|snes} ]; do
    parameters = "$( cat ${runcommand_scripts}/${platform}/retroarch_crt.cfg | awk '{ print $1 }')"
    filename = "/opt/retropie/configs/${platform}/retroarh.cfg";
    file = "$(cat ${filename})"
    for [ p in ${parameters} ]; do
        file = echo "${file}" | grep "${p}"
    done;
    cat "${runcommand_scripts}/${platform}/retroarch_crt.cfg"  > "${filename}"
    echo "${file}" >> "${filename}"
done

#!/bin/bash
if [[ "$(id -u)" -ne 0 ]]; then
    echo "Script must be run under sudo from the user you want to install for. Try 'sudo $0'"
    exit 1
fi

#scripts
runcommand_scripts="resources/opt/retropie/configs"
retropie_configs="/opt/retropie/configs"

cp "resources/usr/bin/chvideo.py" /usr/bin/chvideo && chmod + /usr/bin/chvideo

#Install the boot
config=resources/boot/config.txt
configtxt="$(</boot/config.txt)"
parameters="$(awk -F "=" '{ print $1 }' < "${config}")"
for p in ${parameters} ; do
    configtxt=$(echo "${configtxt}" | grep -v "${p}")
done;
timings="$(chvideo -T 8 -B 8 -L 32 -R 32 -f 60 -i)"
echo "${configtxt}" | grep -v "hdmi_timings" > /boot/config.txt
timings="${timings//60.0/60}"
echo "${timings//s /s=}" >> /boot/config.txt
cat "${config}" >> /boot/config.txt



cp "${runcommand_scripts}"/all/runcommand-*.sh /opt/retropie/configs/all

#Setup console specific files
for f in "${runcommand_scripts}"/* ; do
    if [ -d "$f" ]; then
        platform="${f//${runcommand_scripts}/}"
        conffile=${runcommand_scripts}${platform}/retroarch_ntsc.cfg
        if [ -f "$conffile" ]; then
            parameters="$(awk '{ print $1 }' < "${conffile}")"
            filename="${retropie_configs}${platform}/retroarch.cfg";
            file="$(<"${filename}")"
            for  p in ${parameters} ; do
                file=$(echo "${file}" | grep -v "${p}")
            done;
            cat "${conffile}" > "${filename}"
            echo "${file}" >> "${filename}"
        fi
    fi
done

#Setup emulator specific file
core_options="${retropie_configs}/all/retroarch-core-options.cfg"
options_to_install="${runcommand_scripts}/all/retroarch-core-options_ntsc.cfg"
if [ ! -f "${core_options}" ]; then
    touch "${core_options}";
fi
parameters="$(awk '{ print $1 }' < "${options_to_install}")"
file="$(<"$core_options")"
for p in ${parameters}; do
    file=$(echo "${file}" | grep -v "${p}")
done;
cat "${options_to_install}" >> "${core_options}"
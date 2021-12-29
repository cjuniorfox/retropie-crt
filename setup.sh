#!/bin/bash
if [[ "$(id -u)" -ne 0 ]]; then
    echo "Script must be run under sudo from the user you want to install for. Try 'sudo $0'"
    exit 1
fi

#Install the boot
config=resources/boot/config.txt
configtxt="$(cat /boot/config.txt)"
echo "$configtxt" | grep -v 'overscan_scale\|hdmi_timings\|hdmi_group\|hdmi_mode' > /boot/config.txt
cat "${config}" >> /boot/config.txt

#now the remaining scripts
runcommand_scripts="resources/opt/retropie/configs"
retropie_configs="/opt/retropie/configs"

cp "${runcommand_scripts}"/all/runcommand-*.sh /opt/retropie/configs/all

#Setup console specific files
for f in "${runcommand_scripts}"/* ; do
    if [ -d "$f" ]; then
        platform="${f//${runcommand_scripts}/}"
        conffile=${runcommand_scripts}${platform}/retroarch_crt.cfg
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
options_to_install="${runcommand_scripts}/all/retroarch-core-options.cfg"
if [ ! -f "${core_options}" ]; then
    touch "${core_options}";
fi
parameters="$(awk '{ print $1 }' < "${options_to_install}")"
file="$(<"$core_options")"
for p in ${parameters}; do
    file=$(echo "${file}" | grep -v "${p}")
done;
cat "${options_to_install}" >> "${core_options}"
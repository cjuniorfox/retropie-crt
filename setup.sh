#!/bin/sh
cd /home/pi
sudo apt update -y && sudo apt install git dialog -y
git clone https://github.com/cjuniorfox/retropie-crt.git
cd retropie-crt
cp resources/home/pi/RetroPie/retropiemenu/retropie-crt.sh /home/pi/RetroPie/retropiemenu/retropie-crt.sh
sudo reboot
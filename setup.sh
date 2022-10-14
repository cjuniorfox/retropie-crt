#!/bin/sh
cd /home/pi
sudo apt-get update -y && sudo apt-get install git dialog -y
git clone https://github.com/cjuniorfox/retropie-crt.git || echo "Repository already exists or could not had been cloned."
cd retropie-crt
git pull
cp resources/home/pi/RetroPie/retropiemenu/retropie-crt.sh /home/pi/RetroPie/retropiemenu/retropie-crt.sh
./menu.sh
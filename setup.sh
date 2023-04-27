#!/bin/sh
cd $HOME
sudo apt-get update -y && sudo apt-get install git dialog -y
git clone https://github.com/cjuniorfox/retropie-crt.git || echo "Repository already exists or could not had been cloned."
cd retropie-crt
git pull
cp resources/home/pi/RetroPie/retropiemenu/retropie-crt.sh /home/pi/RetroPie/retropiemenu/retropie-crt.sh
chmod +x /home/pi/RetroPie/retropiemenu/retropie-crt.sh
echo "The initial setup process has been done. At the Pi itself, restart the EmulationStation and access the Retropie-crt option at the Retropie menu."
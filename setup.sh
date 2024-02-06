#!/bin/sh
cd $HOME
sudo apt-get update -y && sudo apt-get install git dialog -y
git clone https://github.com/cjuniorfox/retropie-crt.git || echo "Repository already exists or could not have been cloned."
cd retropie-crt
git pull
mkdir -p $HOME/RetroPie/retropiemenu/
cp resources/home/pi/RetroPie/retropiemenu/retropie-crt.sh $HOME/RetroPie/retropiemenu/retropie-crt.sh
chmod +x $HOME/RetroPie/retropiemenu/retropie-crt.sh
echo "The initial setup process has been done. At the Pi itself, restart the EmulationStation and access the Retropie-crt option at the Retropie menu."

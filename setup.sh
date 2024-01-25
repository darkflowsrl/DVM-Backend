#!/bin/bash

apt install -y python3-pip
apt install -y nodm

echo "startx /usr/bin/chromium --no-sandbox --noerrdialogs --disable-infobars --start-fullscreen --window-size=1270,790  --kiosk https://www.google.com -- -nocursor -dpms -s off -s noblank" >> ~/.bashrc

git clone https://github.com/darkflowsrl/Darkflow-HMI-Backend
cd Darkflow-HMI-Backend

chmod +x disable_gui.sh
bash ./disable_gui.sh

pip3 install -r requirements.txt

reboot


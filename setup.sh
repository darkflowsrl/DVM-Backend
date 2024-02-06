#!/bin/bash

apt install -y python3-pip
apt install -y htop

echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "sleep 2" >> ~/.bashrc
echo "nohup python3 /root/Darkflow-HMI-Backend/main.py > /dev/null 2>1& &" >> ~/.bashrc
echo "startx /usr/bin/chromium --no-sandbox --noerrdialogs --disable-infobars --start-fullscreen --window-size=1270,790  --kiosk https://www.google.com -- -nocursor -dpms -s off -s noblank" >> ~/.bashrc

git clone https://github.com/darkflowsrl/Darkflow-HMI-Backend
cd Darkflow-HMI-Backend

chmod +x disable_gui.sh
bash ./disable_gui.sh


chmod +x 

pip3 install -r requirements.txt

reboot


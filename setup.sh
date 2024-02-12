#!/bin/bash

apt install -y python3-pip
apt install -y htop

echo "sleep 10" >> ~/.bashrc
echo "nohup python3 /root/Darkflow-HMI-Backend/main.py > /dev/null 2>1& &" >> ~/.bashrc
echo "startx /root/Darkflow-HMI-Backend/dvm-app-front-1.0.7.AppImage" >> ~/.bashrc
#echo "startx /usr/bin/chromium --no-sandbox --noerrdialogs --disable-infobars --start-fullscreen --window-size=1270,790  --kiosk https://www.google.com -- -nocursor -dpms -s off -s noblank" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc

git clone https://github.com/darkflowsrl/Darkflow-HMI-Backend/ /root
cd Darkflow-HMI-Backend

wget https://github.com/SegarraFacundo/DVM-front/releases/download/v1.0.7/dvm-app-front-1.0.7.AppImage

systemctl set-default multi-user.target

pip3 install -r requirements.txt

reboot


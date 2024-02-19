#!/bin/bash

apt install -y dist-upgrade
apt install -y python3-pip --fix-missing
apt install -y htop
apt install -y nodm


# /etc/defaults/nodm
# NODM_ENABLED=true
# NODM_USER=root

# nano /etc/systemd/system/getty.target.wants/getty\@tty1.service
# exec: /sbin/getty --autologin ubuntu -8 38400 tty1

echo "sleep 10" >> ~/.bashrc
echo "nohup python3 /root/Darkflow-HMI-Backend/main.py > /dev/null 2>1&" >> ~/.bashrc
echo "startx /root/Darkflow-HMI-Backend/dvm-app-front-1.0.7.AppImage --no-sandbox -- -nocursor" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc

#echo "startx /usr/bin/chromium --no-sandbox --noerrdialogs --disable-infobars --start-fullscreen --window-size=1270,790  --kiosk https://www.google.com -- -nocursor -dpms -s off -s noblank" >> ~/.bashrc
cd /root

git clone https://github.com/darkflowsrl/Darkflow-HMI-Backend/ /root
pip3 install -r requirements.txt

cd Darkflow-HMI-Backend

wget https://github.com/SegarraFacundo/DVM-front/releases/download/v1.0.8/dvm-app-front-1.0.7.AppImage

systemctl set-default multi-user.target


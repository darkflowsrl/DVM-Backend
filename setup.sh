#!/bin/bash

apt install -y software-properties-common
apt install -y dist-upgrade
apt install -y python3-pip --fix-missing
apt install -y htop
apt install -y nodm

VERSION="1.0.9"

# /etc/defaults/nodm
# NODM_ENABLED=true
# NODM_USER=root

# nano /etc/systemd/system/getty.target.wants/getty\@tty1.service
# exec: ExecStart=-/sbin/agetty --noissue --autologin myusername %I $TERM

#echo "startx /usr/bin/chromium --no-sandbox --noerrdialogs --disable-infobars --start-fullscreen --window-size=1270,790  --kiosk https://www.google.com -- -nocursor -dpms -s off -s noblank" >> ~/.bashrc

echo "sleep 5" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "nohup python3 /root/Darkflow-HMI-Backend/main.py > /dev/null 2>1&" >> ~/.bashrc
echo "startx /root/Darkflow-HMI-Backend/dvm-app-front-$VERSION.AppImage --no-sandbox -- -nocursor" >> ~/.bashrc

cd /root

git clone https://github.com/darkflowsrl/Darkflow-HMI-Backend.git /root/Darkflow-HMI-Backend/

cd Darkflow-HMI-Backend

pip3 install -r /root/Darkflow-HMI-Backend/requirements.txt

wget https://github.com/SegarraFacundo/DVM-front/releases/download/v$VERSION/dvm-app-front-$VERSION.AppImage
chmod +x /root/Darkflow-HMI-Backend/dvm-app-front-$VERSION.AppImage

systemctl set-default multi-user.target


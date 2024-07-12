#!/bin/bash

# /etc/defaults/nodm
# NODM_ENABLED=true
# NODM_USER=root
# nano /etc/systemd/system/getty.target.wants/getty\@tty1.service
# exec: ExecStart=-/sbin/agetty --noissue --autologin myusername %I $TERM
# echo "startx /usr/bin/chromium --no-sandbox --noerrdialogs --disable-infobars --start-fullscreen --window-size=1270,790  --kiosk https://www.google.com -- -nocursor -dpms -s off -s noblank" >> ~/.bashrc

timedatectl set-ntp true

#apt -y update
#apt -y upgrade
#apt install -y software-properties-common
apt install -y python3-pip --fix-missing
apt install -y htop
apt install -y nodm

VERSION="1.16.0"
SERVICE_FILE="/etc/systemd/system/getty.target.wants/getty@tty1.service"
NEW_EXECSTART="ExecStart=-/sbin/agetty --noissue --autologin root --noclear %I $TERM"

# ORIGINAL (BAK): -/sbin/agetty -o '-p -- \\u' --noclear %I $TERM

# Backup del servicio
cp "$SERVICE_FILE" "$SERVICE_FILE.bak"

sed -i "s|^ExecStart=.*|$NEW_EXECSTART|" "$SERVICE_FILE"

echo "sleep 5" >> ~/.bashrc

echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc
echo "ip link set can0 up type can bitrate 250000" >> ~/.bashrc

echo "nohup python3 /root/Darkflow-HMI-Backend/main.py > /dev/null 2>1&" >> ~/.bashrc
echo "startx /root/dvm-app-front-$VERSION.AppImage --no-sandbox -- -nocursor" >> ~/.bashrc

cd /root

wget https://github.com/SegarraFacundo/DVM-front/releases/download/v$VERSION/dvm-app-front-$VERSION.AppImage
chmod +x /root/dvm-app-front-$VERSION.AppImage

git clone https://github.com/darkflowsrl/Darkflow-HMI-Backend.git

cd Darkflow-HMI-Backend

pip3 install -r /root/Darkflow-HMI-Backend/requirements.txt

systemctl set-default multi-user.target


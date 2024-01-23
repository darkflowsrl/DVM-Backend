#!/bin/bash

apt install -y python3
apt install -y python3-pip
apt install -y screen

cd /etc
git clone https://github.com/darkflowsrl/Darkflow-HMI-Backend
cd Darkflow-HMI-Backend

pip3 install -r requirements.txt

cp hmi_canbus_server.service /etc/systemd/system/hmi_canbus_server.service

python3 main.py


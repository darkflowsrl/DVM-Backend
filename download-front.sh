#!/bin/bash

VERSION="$1"

cd /root

wget https://github.com/SegarraFacundo/DVM-front/releases/download/v$VERSION/dvm-app-front-$VERSION.AppImage

chmod +x /root/dvm-app-front-$VERSION.AppImage
#!/bin/bash
# Set up chromium and the screen user for local display on the server unit.
clear
function pause(){
   read -p "$*"
}

echo "*****************************************************************************"
echo "*****************************************************************************"
echo "mbtaonbus"
echo "On-bus prediction screen prototype using MBTA API. {not affiliated with the MBTA}"
echo "    Copyright (C) 2019  MICHAEL HAYNES"
echo ""
echo "    This program is free software: you can redistribute it and/or modify"
echo "    it under the terms of the GNU General Public License as published by"
echo "    the Free Software Foundation, either version 3 of the License, or"
echo "    (at your option) any later version."
echo ""
echo "    This program is distributed in the hope that it will be useful,"
echo "    but WITHOUT ANY WARRANTY; without even the implied warranty of"
echo "    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
echo "    GNU General Public License for more details."
echo ""
echo "    You should have received a copy of the GNU General Public License"
echo "    along with this program.  If not, see <https://www.gnu.org/licenses/>."
echo "*****************************************************************************"
echo "*****************************************************************************"
echo ""
echo ""
pause "Press [Enter] to continue..."

# Update packages and setup xorg, lightdm, openbox and chromium   (and reboot)
echo "*****************************************************************************"
echo "running apt-get update/upgrade"
sudo apt update && sudo apt upgrade -y

echo "running apt-get for chromium, openbox, xorg and xinit"
sudo apt-get install --no-install-recommends chromium-browser openbox xorg xinit -y
echo "running apt-get for virtualbox requirements"
sudo apt install build-essential dkms -y

echo "*****************************************************************************"
echo "Set up a user called screen with no password and autologon:"
sudo adduser screen --gecos "" --disabled-password
sudo passwd -d screen  # No password
sudo mkdir -p /home/screen/.config/openbox
sudo cp /home/user/mbtaonbus/system_scripts/autostart.openbox /home/screen/.config/openbox/autostart
sudo chown screen:screen /home/screen/.config/openbox/autostart
sudo chown -R screen:screen /home/screen/.config

# Probably need to write a better script here and WAIT for the server to be up and running:
sudo cp /home/user/mbtaonbus/system_scripts/screen_bash_profile /home/screen/.bash_profile
sudo chown screen:screen /home/screen/.bash_profile

# Setup the Autologon:
sudo mkdir /etc/systemd/system/getty@tty1.service.d
sudo cp /home/user/mbtaonbus/system_scripts/autologon /etc/systemd/system/getty@tty1.service.d/override.conf

# Set up Grub:
sudo cp /home/user/mbtaonbus/system_scripts/grub.defaults /etc/default/grub
sudo update-grub

# Turn off all messages at logon:
sudo chmod -x /etc/update-motd.d/*
sudo touch /home/screen/.hushlogin

echo "*****************************************************************************"
echo "Install Virtual Box Guest Additions"
./VBoxLinuxAdditions.sh

echo "*****************************************************************************"
echo "REBOOT...."

echo -n "Reboot? (y/n)?" && read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    sudo reboot
fi


#mbtaonbus
#On-bus prediction screen prototype using MBTA API. {not affiliated with the MBTA}
#    Copyright (C) 2019  MICHAEL HAYNES
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

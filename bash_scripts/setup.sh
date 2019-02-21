#!/bin/bash
# Main setup script to run on an empty Ubuntu server 16.04 server.
# Written by M. Haynes January 2019

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

echo "*****************************************************************************"
echo "Extracting web_static tar in root of home directory"
cd ~
cp ~/mbtaonbus/web_static.tar.gz .
tar -xf web_static.tar.gz
cd ~/mbtaonbus/bash_scripts

echo "*****************************************************************************"
echo "running apt-get update/upgrade"
sudo apt-get update
sudo apt-get -y upgrade

echo "*****************************************************************************"
echo "running apt-get install"
sudo apt-get -y install python3-pip python3-venv nginx unzip

echo "*****************************************************************************"
echo "create directories"
mkdir /home/user/mbtaonbus/data
mkdir /home/user/mbtaonbus/logs

echo "*****************************************************************************"
echo "Set hostname"
sudo hostnamectl set-hostname mbtaonbus
echo "Might also need to edit /etc/hosts file"

echo "*****************************************************************************"
echo "Setting up Virtual Python Environment:"
python3 -m venv ~/mbtaonbus/venv
source ~/mbtaonbus/venv/bin/activate
pip install --upgrade pip
pip install uwsgi flask pandas

echo "*****************************************************************************"
echo "Setting up Web Service:"
sudo cp ~/mbtaonbus/system_scripts/mbtaonbus.service /etc/systemd/system/.

sudo systemctl start mbtaonbus
sudo systemctl enable mbtaonbus
sudo systemctl daemon-reload  # important anytime script is rerun

echo "*****************************************************************************"
echo "Setting up NGINX proxy gateway"
sudo cp ~/mbtaonbus/system_scripts/mbtaonbus.nginx /etc/nginx/sites-available/mbtaonbus

sudo ln -s /etc/nginx/sites-available/mbtaonbus /etc/nginx/sites-enabled
sudo nginx -t

sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'

echo "*****************************************************************************"
echo "Now Refresh MBTA data"
/home/user/mbtaonbus/bash_scripts/refresh_mbta_gtfs.sh

echo "*****************************************************************************"
echo "Set up refresh_mbta_gtfs.sh as a cron job"
(crontab -l 2>/dev/null; echo "@reboot ~/mbtaonbus/bash_scripts/refresh_mbta_gtfs.sh > /home/user/mbtaonbus/logs/gtfsrefresh 2>&1") | crontab -

echo "*****************************************************************************"
echo "Set up symlinks to log data in the log directory:"
ln -s /tmp/errlog ~/mbtaonbus/logs/flask.errlog
ln -s /tmp/reqlog ~/mbtaonbus/logs/flask.reqlog

echo "*****************************************************************************"
echo "Set up symlinks to web_static code repositories:"
ln -s ~/web_static/js/jquery-3.3.1.min.js ~/mbtaonbus/static/js/.
mkdir ~/mbtaonbus/static/cssc
ln -s ~/web_static/css/* ~/mbtaonbus/static/css/.
ln -s ~/web_static/leaflet ~/mbtaonbus/static/.

echo "*****************************************************************************"
echo "Copy in a variables.env file if it exists in the root of the home:"
cp ~/variables.env ~/mbtaonbus/.

echo "*****************************************************************************"
echo ""
echo "REBOOT!!  run sudo reboot"
echo ""
echo "Go to http://mbtaonbus and select a bus"

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


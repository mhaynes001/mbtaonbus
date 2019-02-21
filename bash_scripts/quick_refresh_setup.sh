#!/bin/bash
# Main setup script to run on an empty Ubuntu server 16.04 server.
# Written by M. Haynes January 2019

echo "*****************************************************************************"
echo "running apt-get update/upgrade"
sudo apt-get update
sudo apt-get -y upgrade

echo "*****************************************************************************"
echo "create directories"
mkdir /home/user/mbtaonbus/data
mkdir /home/user/mbtaonbus/logs

echo "*****************************************************************************"
echo "Setting up Virtual Python Environment:"
python3 -m venv ~/mbtaonbus/venv
source ~/mbtaonbus/venv/bin/activate
pip install --upgrade pip
pip install uwsgi flask pandas

echo "*****************************************************************************"
echo "Now Refresh MBTA data"
/home/user/mbtaonbus/bash_scripts/refresh_mbta_gtfs.sh

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

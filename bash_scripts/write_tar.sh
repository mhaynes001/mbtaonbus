#!/bin/bash
# Scrpit to clean up the folder and create a tar file for backup/sharing
# Written by M. Haynes Feb 2019

echo "*****************************************************************************"
echo "Deleteing data to clean up directory"
rm -r ~/mbtaonbus/data/
rm -r ~/mbtaonbus/logs/
rm -r ~/mbtaonbus/__pycache__/
rm -r ~/mbtaonbus/venv/
rm -r ~/mbtaonbus/mbtaonbus.sock

echo "cleaning variables.env file"
sed -i 's/MBTA_KEY.*/MBTA_KEY=<yourkey>/g' ~/mbtaonbus/variables.env
sed -i 's/MAPBOX_KEY.*/MAPBOX_KEY=<yourkey>/g' ~/mbtaonbus/variables.env

echo "Creating compressed TAR archive"
cd ~
tar -czf mbtaonbus.tar.gz -P mbtaonbus/

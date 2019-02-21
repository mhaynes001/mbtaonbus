#!/bin/bash

# Run on a schedule in a crontab (or on starup), check for new schedule file by downloading and comparing MD5 string
#  The -nv supresses the progress bar so it does not show up in the crontab log output
wget -nv https://cdn.mbta.com/MBTA_GTFS.zip -O /home/user/mbtaonbus/data/MBTA_GTFS.zip

if md5sum --status -c /home/user/mbtaonbus/data/MBTA_GTFS.md5; then
     echo "No update needed"
     exit 0
fi

echo "Only get MBTA data if needed"
rm /home/user/mbtaonbus/data/*.txt
rm /home/user/mbtaonbus/data/*.md5

source /home/user/mbtaonbus/venv/bin/activate #activate the python environment
# Get MBTA data:
unzip -j -o "/home/user/mbtaonbus/data/MBTA_GTFS.zip" "shapes.txt" -d "/home/user/mbtaonbus/data"
unzip -j -o "/home/user/mbtaonbus/data/MBTA_GTFS.zip" "stops.txt" -d "/home/user/mbtaonbus/data"
unzip -j -o "/home/user/mbtaonbus/data/MBTA_GTFS.zip" "stop_times.txt" -d "/home/user/mbtaonbus/data"
unzip -j -o "/home/user/mbtaonbus/data/MBTA_GTFS.zip" "trips.txt" -d "/home/user/mbtaonbus/data"
unzip -j -o "/home/user/mbtaonbus/data/MBTA_GTFS.zip" "routes.txt" -d "/home/user/mbtaonbus/data"
unzip -j -o "/home/user/mbtaonbus/data/MBTA_GTFS.zip" "route_patterns.txt" -d "/home/user/mbtaonbus/data"
unzip -j -o "/home/user/mbtaonbus/data/MBTA_GTFS.zip" "shapes.txt" -d "/home/user/mbtaonbus/data"
# Process the data:
python3 /home/user/mbtaonbus/mbta_gtfs.py
mv /home/user/mbtaonbus/data/mbta_rail_data.js /home/user/mbtaonbus/static/js/
rm /home/user/mbtaonbus/data/stop_times.txt   # Saves space
# Save the MD5sum for future checking:
md5sum /home/user/mbtaonbus/data/MBTA_GTFS.zip > /home/user/mbtaonbus/data/MBTA_GTFS.md5

# Restart the website service now that the data updated.
/home/user/mbtaonbus/bash_scripts/flask_restart.sh

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

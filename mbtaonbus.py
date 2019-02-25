# mbtaonbus
# preds.py
# Created by M. Haynes
# Late July 2018 & January 2019 (Flask)
#

import main_functions as mf
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
# Main index page returns a list of active buses to choose from for demo:
def index():
	return render_template('buslist.html',veh_list=mf.getvehicles())

@app.route("/preds/<string:bus>/")
# The main page with bus current route info and prediction grid with map:
def preds(bus):
	veh_data = mf.getbasicdata(bus)
	if veh_data is not None:
		# Go get the predictions, shape and alerts and store in a data dictionary:
		data_dict = {"veh_data": veh_data,
				     "pred_data": mf.getpredictions(veh_data["trip_id"]),
		 			 "shape_data": mf.getshape(veh_data["shape_id"]),
		 			 "alert_data": mf.getalerts(veh_data["route_id"]),
		 			 "map_data": mf.getmapboxkey(),
		 			 "stop_data": mf.getstops(veh_data["trip_id"])
		 			 }
		# Should probably test for prediction data as well before continuing:
		return render_template('preds.html',data=data_dict)
	else:
		# Bus not in service, return the no predictions page.
		return render_template('nopreds.html',bus=bus)

@app.route("/preds-dark/<string:bus>/")
# The main page with bus current route info and prediction grid with map:
def preds_dark(bus):
	veh_data = mf.getbasicdata(bus)
	if veh_data is not None:
		# Go get the predictions, shape and alerts and store in a data dictionary:
		data_dict = {"veh_data": veh_data,
				     "pred_data": mf.getpredictions(veh_data["trip_id"]),
		 			 "shape_data": mf.getshape(veh_data["shape_id"]),
		 			 "alert_data": mf.getalerts(veh_data["route_id"]),
		 			 "map_data": mf.getmapboxkey(),
		 			 "stop_data": mf.getstops(veh_data["trip_id"])
		 			 }
		# Should probably test for prediction data as well before continuing:
		return render_template('preds-dark.html',data=data_dict)
	else:
		# Bus not in service, return the no predictions page.
		return render_template('nopreds.html',bus=bus)

# Not sure if this is required or not for the main Flask application:
if __name__ == "__main__":
    app.run()

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


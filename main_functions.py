# mbtaonbus
# main_functions.py
# Created by M. Haynes
# Late July 2018 & January 2019 (Flask)
#

from urllib.request import Request, urlopen
import gzip, json, datetime, urllib, math, os
import pandas as pd

# Get the MBTA API key from the system variables:
apikey = os.environ.get('MBTA_KEY')
mainurl='https://api-v3.mbta.com/'
data_path = '/home/user/mbtaonbus/data/'

def getmapboxkey():
    map_parms = {"mapbox_key": os.environ["MAPBOX_KEY"],
                 "mapbox_user": os.environ["MAPBOX_USER"],
                 "mapbox_style": os.environ["MAPBOX_STYLE"]}
    return map_parms

# Route Data:
route_data = pd.read_csv(data_path+'routes2.txt')

# Stop Data:
stop_data = pd.read_csv(data_path+'stops2.txt')

# Shape Data:
shape_data = pd.read_csv(data_path+'shapes2.txt')
shape_data = shape_data.round({'shape_pt_lat': 6, 'shape_pt_lon': 6})

# Trip Pattern Data:
trip_patterns = pd.read_csv(data_path+'trip_patterns.txt', dtype={'trip_id': int, 'pattern': int, 'shape_id': str})

# Unique Patterns:
unique_stopstrings = pd.read_csv(data_path+'unique_stopstrings.txt', dtype={'pattern': int, 'stops': str})
unique_stopstrings.stops.apply(lambda x: x[1:-1].split(',') )

#Function that gets data compressed and then uncompresses it to JSON, returns JSON:
def apiget(midurl,endurl=''):
    fullurl = mainurl + midurl + '?api_key=' + apikey + endurl
    req = Request(fullurl)
    req.add_header('Accept-Encoding', 'gzip')
    try:
        response = urlopen(req)
    except:
        return  # Ideally return an error code here and then print a different page
    try:
        content = gzip.decompress(response.read())    # If it fails run the uncompressed version
    except:
        return
    json_out = json.loads(content.decode('utf-8'))
    return json_out

# Sometimes it won't compress so this is for those times, returns JSON
def apiget_nocompress(midurl,endurl=''):
    fullurl=mainurl+midurl+'?api_key='+apikey+endurl
    request = urllib.request.urlopen(fullurl)
    json_out = json.loads(request.read().decode())
    return json_out

# Function to convert time to a nice string for presentation:
def converttime(time_in):
    if time_in is None: return
    if time_in[-3:-2] == ":":
        time_in = time_in[:-3]+time_in[-2:]  #remove the last colon from UTC offset
    time_out = datetime.datetime.strptime(time_in,"%Y-%m-%dT%H:%M:%S%z")
    time_out = time_out.strftime('%-I:%M:%S')
    return time_out

# Function to look up data and return a dictionary of attributes:
def getdata(data,id_col,id_in):
    try:
        output = data[data[id_col] == str(id_in)].to_dict('records')[0]
    except:
        output = {}
    return output

# Function to return the ordinal version of a number:   (I have no idea how this works!)
# Found: https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement 
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

# Function to return a string even if None:
xstr = lambda s: '' if s is None else str(s)

# Function to return a list of active vehicles (for the main page to select a bus)
def getvehicles():
    veh_list = []
    veh_data = apiget('vehicles')
    for i in range(50):   ### Need to fix this to list all buses, need to get the count
        if veh_data['data'][i]['id'][0] == 'y':
            veh_list.append(veh_data['data'][i]['id'][1:])
    return veh_list

# Function to get the basic bus data (test for data to ensure it is out there)
def getbasicdata(veh):
    veh_data = apiget('vehicles/y'+str(veh))
    if veh_data is not None:
        return processveh_data(veh_data)
    else:
        return

# Function to process the data into dictionary for webpage.
def processveh_data(veh_data):
    # Current time:
    currentDT = datetime.datetime.now() # + datetime.timedelta(hours=1)  # +1 to get to EST

    # Get the Trip Data from the API:
    trip_id =  veh_data['data']['relationships']['trip']['data']['id']
    trip_data = apiget('trips/'+trip_id)

    # Current Bus details:
    try:
        route_id = veh_data['data']['relationships']['route']['data']['id']
    except:
        route_id = '0'
    try:
        dir_id = veh_data['data']['attributes']['direction_id']
    except:
        dir_id = 0
    try:
        stop_id = veh_data['data']['relationships']['stop']['data']['id']
    except:
        stop_id = 0

    try:
    	shape_id = trip_data['data']['relationships']['shape']['data']['id']
    except:
        shape_id = 0

    lat = veh_data['data']['attributes']['latitude']
    long = veh_data['data']['attributes']['longitude']
    heading = veh_data['data']['attributes']['bearing']
    location = str(lat) +','+ str(long) +','+ str(heading)
    current_status = veh_data['data']['attributes']['current_status']

    veh_data_out = {
        "vehicle_number" : int(veh_data['data']['attributes']['label']),
        "lat" : lat, "long" : long, "heading" : heading, "location" : location,
	"updated_at" : converttime(veh_data['data']['attributes']['updated_at']),
	"current_time" : currentDT.strftime('%-I:%M:%S %p'),
	"current_status" : current_status.replace("_", " ").lower(),

	"route_id" : route_id, "dir_id" : dir_id,
	"stop_id" : stop_id,
	"stop" : str.upper(xstr(getdata(stop_data,'stop_id',stop_id).get("stop_name"))),
	"trip_id" : trip_id,

	"route_name" : getdata(route_data,'route_id',route_id).get('route_short_name'),
	"route_des" : getdata(route_data,'route_id',route_id).get('route_long_name'),

	"headsign" : trip_data['data']['attributes']['headsign'],
	"shape_id" : shape_id
    }
    return veh_data_out

# Function to get the predictions and return a dictionary (ideally of size 8)
def getpredictions(trip_id):
	pred_results = apiget('predictions','&filter[trip]='+trip_id)
	pred_data = []
	n = 0  # The prediction position in the main list
	m = 0  # The prediction position in what is returned

	## Get the length of the pred_results array and evenly obtain 8 predictions
	## If an odd number should not show stop #8 so that we always have 8
	try:
		pred_length = len(pred_results['data'])
	except:
		pred_length = 0
		return
	factor = math.trunc(pred_length/8)+1
	if pred_length < 10: factor = 1  # If 9 or less factor is 1
	# Can just make the array so it essentially is and n in []
	# Special case array for six n values. store them in another array.

	for result in pred_results['data']:
		n += 1
		arr_time = converttime(result['attributes']['arrival_time'])
		dep_time = converttime(result['attributes']['departure_time'])
		time = dep_time if arr_time is None else arr_time
		stop_id = result['relationships']['stop']['data']['id']

		if time is not None and (n%factor == 0 or n == pred_length or n == 1):
			m += 1
		    # Drop the seconds but add a "+" if it is over 30 seconds (2nd half of minute)
			time = time[:-3] if int(time[-2:]) < 30 else time[:-3]+'+'
			pred_data.append({
				"m" : m,  # Dictionary index
    			"n" : n,  # Overall prediction index
    			"n_txt" : ordinal(n), # Prediction as a ordinal number
    			"stop_seq" : result['attributes']['stop_sequence'],
    			"stop_id" : stop_id,
    			"stop" : str.upper(getdata(stop_data,'stop_id',stop_id).get("stop_name")),
    			"time" : time
    		})

	if pred_data[0]["n_txt"] == '1st': pred_data[0]["n_txt"] = 'Next'

	#If pred_data length is 9 drop the 8th item:
	if len(pred_data) > 8:
		del pred_data[7]
	# If pred_data length is 7 slide 2nd back into the dictionary:

	return pred_data

# Function to return the shape of a route from the GTFS shape.txt file in a pandas df:
def getshape(shape_id):
#	print("shapeID:",shape_id)
	shape = shape_data[shape_data.shape_id == shape_id].values
        # SHOULD round lat/longs
	return shape

# Function to return the stops of a given trip:
def getstops(trip_id_in):
    #stop_ids = []
    # Get the stop ids for the trip (used to take forever!):
    try:
        pattern = trip_patterns[trip_patterns.trip_id == int(trip_id_in)]['pattern'].values[0]
    except:
        pattern = 0
        stops = []
        return stops

    stop_ids = unique_stopstrings[unique_stopstrings.pattern == pattern]['stops'].values[0][1:-1].split(',')

    # Get the stop lat/long from the stops_data dataframe:
    stops = stop_data[stop_data.stop_id.isin(stop_ids)].values
    # SHOULD uppercase stop name
    return stops

# Function to return the alerts for a given route:
def getalerts(route_id):
	alert_data = apiget('alerts','&filter[route]='+route_id)
	if alert_data is not None:
		alert = alert_data['data'][0]['attributes']['short_header']
	else:
		alert = ""
	return alert

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

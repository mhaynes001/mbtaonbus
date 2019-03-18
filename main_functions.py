# mbtaonbus
# main_functions.py
# Created by M. Haynes
# Late July 2018 & January 2019 now Feb 2019 (GTFS-rt) (Flask)
#

from google.transit import gtfs_realtime_pb2 as gtfs_rt
from protobuf_to_dict import protobuf_to_dict as pb_to_dict
import math, os, requests as req, datetime as dt, pandas as pd

def timestamp_convert(posix_time):
    return dt.datetime.fromtimestamp(posix_time).strftime('%H:%M:%S')

veh_feed = gtfs_rt.FeedMessage()
trip_feed = gtfs_rt.FeedMessage()
alert_feed = gtfs_rt.FeedMessage()

# Get the URL from the system variables:
#mainurl=   #os.environ.get('GTFS_URL')
gtfs_rt_url = 'https://cdn.mbta.com/realtime/'
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
    veh_response = req.get(gtfs_rt_url+'VehiclePositions.pb')
    veh_feed.ParseFromString(veh_response.content)
    # convert to dict from protobuf feed
    veh_dict = pb_to_dict(veh_feed)

    veh_list = []
    for x in veh_dict['entity']:
        veh_list.append(x['vehicle']['vehicle']['label'])
    return veh_list

# Function to get the basic bus data (test for data to ensure it is out there)
def getbasicdata(veh):
    veh_response = req.get(gtfs_rt_url+'VehiclePositions.pb')
    veh_feed.ParseFromString(veh_response.content)
    # convert to dict from protobuf feed
    veh_dict = pb_to_dict(veh_feed)
    veh_match = next((x for x in veh_dict['entity'] if x['vehicle']['vehicle']['label'] == veh), 'None')
    veh_match = veh_match['vehicle']

    if veh_match is not None:
        return processveh_data(veh_match)
    else:
        return

# Function to process the data into dictionary for webpage.
def processveh_data(veh_data):
    # Current time:
    currentDT = dt.datetime.now() # + datetime.timedelta(hours=1)  # +1 to get to EST

    route_id = veh_data['trip']['route_id']
    trip_id = veh_data['trip']['trip_id']
    print('trip_id:',trip_id)
    shape_id =  getdata(trip_patterns,'trip_id',trip_id).get('shape_id')
    shape_id = 7430010
    print('shape_id:',shape_id)
    lat = round(veh_data['position']['latitude'],6)
    long = round(veh_data['position']['longitude'],6)
    heading = veh_data['position']['bearing']
    location = str(lat) +','+ str(long) +','+ str(heading)
    current_status = veh_data['current_status']   ### Need to look these up.

    veh_data_out = {
        "vehicle_number" : veh_data['vehicle']['label'],
        "lat" : lat, "long" : long, "heading" : heading, "location" : location,
        "updated_at" : timestamp_convert(veh_data['timestamp']),
        "current_time" : currentDT.strftime('%-I:%M:%S %p'),
        "current_status" : current_status,  #.replace("_", " ").lower()

        "route_id" : route_id,
        "dir_id" : veh_data['trip']['direction_id'],
        "stop_id" : veh_data['stop_id'],
        "stop" : str.upper(xstr(getdata(stop_data,'stop_id',veh_data['stop_id']).get("stop_name"))),
        "trip_id" : trip_id,

        "route_name" : getdata(route_data,'route_id',route_id).get('route_short_name'),
        "route_des" : getdata(route_data,'route_id',route_id).get('route_long_name'),
        "headsign" : '',  ## Does not exist in GTFS-rt feed
        "shape_id" : shape_id
    }
    return veh_data_out

# Function to get the predictions and return a dictionary (ideally of size 8)
def getpredictions(trip_id):
    trip_response = req.get(gtfs_rt_url+'TripUpdates.pb')
    trip_feed.ParseFromString(trip_response.content)
    trip_dict = pb_to_dict(trip_feed)

    trip_match = next((x for x in trip_dict['entity'] if x['id'] == trip_id), None)
    try:
        pred_results = trip_match['trip_update']['stop_time_update']
    except:
        return

    pred_data = []
    n = 0  # The prediction position in the main list
    m = 0  # The prediction position in what is returned

    ## Get the length of the pred_results array and evenly obtain 8 predictions
    ## If an odd number should not show stop #8 so that we always have 8
    pred_length = len(pred_results)
    factor = math.trunc(pred_length/8)+1

    if pred_length < 10: factor = 1  # If 9 or less factor is 1
    # Can just make the array so it essentially is and n in []
    # Special case array for six n values. store them in another array.

    for result in pred_results:
        n += 1
        if 'arival' in result.keys():
            time = timestamp_convert(result['arival']['time'])
        if 'departure' in result.keys():
            time = timestamp_convert(result['departure']['time'])
        stop_id = result['stop_id']

        if time is not None and (n%factor == 0 or n == pred_length or n == 1):
            m += 1
            # Drop the seconds but add a "+" if it is over 30 seconds (2nd half of minute)
            time = time[:-3] if time[-2:] < '30' else time[:-3]+'+'
            pred_data.append({
                "m" : m,  # List index
                "n" : n,  # Overall prediction index
                "n_txt" : ordinal(n), # Prediction as a ordinal number
                "stop_seq" : result['stop_sequence'],
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
	#alert_data = apiget('alerts','&filter[route]='+route_id)
	alert_data = None   # For now turn this off...
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

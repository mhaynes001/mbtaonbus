#!/usr/bin/python
import pandas as pd
import os, sys

# The data path, should generate this dynamically:
data_path = '/home/user/mbtaonbus/data/'

## Read in GTFS data files (define datatypes first):
dtype_trips = {
	'route_id': str, 'service_id': str, 'trip_id': str, 'trip_headsign': str,
	'trip_short_name': str, 'direction_id': object, 'block_id': str, 'shape_id': str,
	'wheelchair_accessible': object, 'trip_route_type': object, 'route_pattern_id': str,
	'bikes_allowed': object }
trips = pd.read_csv(data_path+'trips.txt', dtype=dtype_trips)

dtype_routes = {
	'route_id': str, 'agency_id': int, 'route_short_name': str, 'route_long_name': str,
	'route_desc': str, 'route_fare_class': str, 'route_type': int, 'route_url': str,
	'route_color': str, 'route_text_color': str,'route_sort_order': int, 'line_id': object,
	'listed_route': str }
routes = pd.read_csv(data_path+'routes.txt', dtype=dtype_routes)

dtype_patterns = {
	'route_pattern_id': str, 'route_id': str, 'direction_id': int,
	'route_pattern_name': str, 'route_pattern_time_desc': str,
	'route_pattern_typicality': int, 'route_pattern_sort_order': str,
	'representative_trip_id': str }
route_patterns = pd.read_csv(data_path+'route_patterns.txt', dtype=dtype_patterns)

dtype_shapes = {
	'shape_id': str, 'shape_pt_lat': float, 'shape_pt_lon': float,
	'shape_pt_sequence': int, 'shape_dist_traveled': float }
shapes = pd.read_csv(data_path+'shapes.txt', dtype=dtype_shapes)

dtype_stops = {
	'stop_id': str, 'stop_code': str, 'stop_name': str, 'stop_desc': str,
	'platform_code': object, 'platform_name': str, 'stop_lat': float, 'stop_lon': float,
	'zone_id': str, 'stop_address': str, 'stop_url': str, 'level_id': object,
	'location_type': object, 'parent_station': str, 'wheelchair_boarding': object }
stops = pd.read_csv(data_path+'stops.txt', dtype=dtype_stops)

########  Rail Lines & Stations (export to javascript file)
# Route Data for Rail Lines only:
rail_routes = routes[routes.route_type.isin([0,1])]
# Route Patterns (only the ones that are typically used)
rail_patterns = route_patterns[route_patterns.route_id.isin(rail_routes['route_id'])]
rail_patterns = rail_patterns[rail_patterns.route_pattern_typicality == 1]
# Join the Routes and patterns together:
rail_patterns = rail_patterns.set_index('route_id').join(rail_routes.set_index('route_id'))

# Remove the blank route_pattern_id columns from trip data:
trips = trips[pd.notnull(trips['route_pattern_id'])]  # Remove NaN route_pattern_ids
# Get just the rail trips:
rail_trips = trips[trips.route_pattern_id.isin(rail_patterns.route_pattern_id)]
# Count the rail trips by route and shape:  (delete any not really used)
rail_shapes_cnt = rail_trips.groupby(['route_pattern_id','shape_id'])['route_id'].count()
rail_shapes_cnt = rail_shapes_cnt.reset_index(name="count")
rail_shapes_cnt = rail_shapes_cnt[rail_shapes_cnt['count'] > 10].dropna()
# Join the route shape and count data with the rail pattern data:
rail_patterns = rail_patterns.set_index('route_pattern_id').join(
    rail_shapes_cnt.set_index('route_pattern_id'))
# Cleanup work:
rail_patterns = rail_patterns[['route_long_name','direction_id','route_color',
                               'shape_id','count','representative_trip_id']].reset_index()
rail_patterns = rail_patterns.drop_duplicates()
col_list = ['route_long_name','route_color','shape_id','representative_trip_id']
# Only really need the one direction
rail_shape_list = rail_patterns[rail_patterns.direction_id == 1][col_list]
# Make a dataframe of just the shapes that are rail lines
rail_shapes = shapes[shapes.shape_id.isin(rail_shape_list['shape_id'])]

# Open a file to write:
w = open(data_path+'mbta_rail_data.js','w')
w.writelines('//Rail Lines:\n')

print('Exporting Rail shapes')
# Loop through rail_shape_list and export to a file in leaflet javascript:
pline_options = "', opacity: 0.8, weight: 4 }).addTo(map);\n"
for index, row in rail_shape_list.iterrows():
    # Generate a Line Name to use as a variable/label:
    #   (First word of the long name as the linename)
    line = row[0].split()[0]
    #Green Line branch! (Get the last character for the Branch)
    if len(row[0].split()) >2: line = line+row[0].split()[2]
    # Add in the first three digits of the shape ID for uniqueness
    line = line+row[2].split('_')[0]

    print('Exporting line:', row['shape_id'], line)
    x_cols = ['shape_pt_lat','shape_pt_lon']
    # A dataframe of the rail shape for the given shape_id rounded to 6 places:
    x = rail_shapes[rail_shapes.shape_id == row['shape_id']][x_cols].round(6)
    # Build an array of the rail line points:
    x_array = '['
    for index, a in x.iterrows():
        x_array = x_array+'['+str(a.shape_pt_lat)+','+str(a.shape_pt_lon)+'],'
    # Remove trailing comma and add final close bracket ]
    x_array = x_array[:-1]+']'
    # Write to the mbta_rail_data.js file:
    w.writelines('var'+line+'='+x_array+';\n')
    w.writelines("L.polyline(var"+line+", {color: '#"+row[1]+pline_options)
    w.writelines("\n")  # A new line between each rail line

# Build a list of rail stations and add to javascript export
print("Exporting Stations:...")   # Stations are essentially stops that start with "place"
stop_columns = ['stop_id','stop_name','stop_lat','stop_lon']
rail_stops = stops[stops['stop_id'].str.startswith('place')][stop_columns]
rail_stops = rail_stops.round(6)
rail_stops

# Loop through the stations and export in javascript format:
w.writelines('//Rail Stations:\n')
for index, row in rail_stops.iterrows():
    marker = 'L.marker(['+str(row.stop_lat)+','+str(row.stop_lon)+'], '
    marker = marker+'{icon: TIcon}).bindTooltip("'+str.upper(row.stop_name)
    marker = marker+'").addTo(map);\n'
    w.writelines(marker)
w.close()

#####  EXPORT smaller files of the route, stop and shape data:
print("Exporting smaller files...")
# Route Data:
route_data = routes[['route_id','route_short_name','route_long_name','route_desc']]
route_data.to_csv(data_path+'routes2.txt', index_label='row_id')

# Stop Data:
stop_data = stops[['stop_id','stop_name','stop_lat','stop_lon']]
stop_data.to_csv(data_path+'stops2.txt', index_label='row_id')

# Shape Data:
shape_data = shapes[['shape_id','shape_pt_lat','shape_pt_lon']]
shape_data = shape_data.round({'shape_pt_lat': 6, 'shape_pt_lon': 6})
shape_data.to_csv(data_path+'shapes2.txt', index_label='row_id')

##### CREATE stop strings and patterns:
print("Creating Stop Strings and Patterns")
dtype_stoptimes = {
    'trip_id': str, 'arrival_time': str, 'departure_time': str, 'stop_id': str,
    'stop_sequence': int, 'stop_headsign': str, 'pickup_type': int, 'drop_off_type': int,
    'timepoint': str, 'checkpoint_id': str }
stop_times = pd.read_csv(data_path+'stop_times.txt', dtype=dtype_stoptimes)

trip_stops = stop_times[['trip_id','stop_id']]
trip_stops = trip_stops[trip_stops.stop_id.apply(lambda x: x.isnumeric())]
trip_stops = trip_stops[trip_stops.trip_id.apply(lambda x: x.isnumeric())]
trip_stops = trip_stops.astype({'trip_id': int, 'stop_id': int})

print('trip_stops:',trip_stops.shape)
print('stop_times:',stop_times.shape)
print('Unique stops:',trip_stops.stop_id.unique().size )
print('Unique trips:',trip_stops.trip_id.unique().size )

# A flatten function to flatten a nested array:
flatten = lambda array: [item for sublist in array for item in sublist]
trip_stop_arrays = []
stop_col = ['stop_id']

# Generate the trip stop arrays:  THIS TAKES A LONG TIME!!!
print("Generate trip stop arrays... This takes a LONG time (3-5 minutes)!")  #### LONG PROCESS!
for a in trip_stops.trip_id.unique():
    b = flatten(trip_stops[trip_stops.trip_id == a][stop_col].values.astype(int).tolist())
    c = [int(a),str(b).replace(" ", "")]
    trip_stop_arrays.append(c)

# Set as dataframe for export:
trip_stops_df = pd.DataFrame(trip_stop_arrays,columns=['trip_id','stops'])

print('trip_stops:',trip_stops_df.shape)
print('trip_stops unique:',trip_stops_df.stops.unique().size)

unique_stopstrings = pd.DataFrame(trip_stops_df.stops.unique(), columns=['stops'])
unique_stopstrings['pattern'] = unique_stopstrings.index
unique_stopstrings[['pattern', 'stops']].to_csv(data_path+'unique_stopstrings.txt', index=False)


#trip_patterns = pd.merge(trip_stops_df, unique_stopstrings, on='stops')
trips = trips[trips.trip_id.apply(lambda x: x.isnumeric())]
trips = trips.astype({'trip_id': int})
trip_patterns = trip_stops_df.merge(unique_stopstrings, on='stops').merge(trips, on='trip_id')
trip_patterns[['trip_id', 'pattern', 'shape_id']].to_csv(data_path+'trip_patterns.txt', index=False)

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


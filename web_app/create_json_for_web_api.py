# %%
import geojson
import csv
from collections import defaultdict
import json

# %% md
# PARAMETERS
## Define path of data source file:
# - SIRI_EXPORTED_FROM_SPLUNK -> siri data about real time bus locations
# - GTFS_STAT_EXPORTED_FROM_SPLUNK -> static data about the route and the trip
# - SHAPE_FILE_7716 -> data about the shape of the bus route
# %%
# SIRI_EXPORTED_FROM_SPLUNK = '/home/aviv/Downloads/siri_149_two_directions_30_days.csv'
# GTFS_STAT_EXPORTED_FROM_SPLUNK = '/home/aviv/Downloads/gtfs_stat_149_two_directions_30_days.csv'
# SHAPE_FILE_7716 = '/home/aviv/Downloads/route_id_7716_shape_id_93603.csv'
SIRI_EXPORTED_FROM_SPLUNK = 'D:\Downloads\web_app\siri_149.csv'
GTFS_STAT_EXPORTED_FROM_SPLUNK = 'D:\Downloads\web_app\gtfs_149.csv'
SHAPE_FILE_7716 = 'D:/Downloads/web_app/route_id_7716_shape_id_93603.csv'


# %% md
# SIRI Objects
# %%
## SIRI

class SiriKey():
    def __init__(self, date, planned_start_time, route_id, route_short_name):
        self.date = date
        self.planned_start_time = planned_start_time
        self.route_id = route_id
        self.route_short_name = route_short_name

    def _tuple(self):
        return (self.date, self.planned_start_time, self.route_id, self.route_short_name)

    def __eq__(self, other):
        return self._tuple() == other._tuple()

    def __lt__(self, other):
        return (self.date, self.route_id) < (other.date, other.route_id)

    def __hash__(self):
        return self._tuple().__hash__()

    def __repr__(self):
        return 'SiriKey: ' + "@".join(self._tuple())

    @staticmethod
    def of_csv_row(csv_row_dict):
        return SiriKey(csv_row_dict['timestamp'][:10], csv_row_dict['planned_start_time'],
                       csv_row_dict['route_id'], csv_row_dict['route_short_name'])


class SiriTrip():
    def __init__(self, key, geojson_feature_collection):
        self.key = key
        self.geojson_feature_collection = geojson_feature_collection

    def __repr__(self):
        return 'SiriTrip: ' + str(self.key)

    # function to return the second element of the
    # two elements passed as the parameter
    @staticmethod
    def sort_by_lat(val):
        return val["lat"]

    @staticmethod
    def of_csv_rows(key, rows):
        # sort rows of the specific route_id by time from midnight to midnight
        rows.sort(key=lambda item: item['time_recorded'])

        features = [geojson.Feature(geometry=geojson.Point([float(row['lat']), float(row['lon'])]),
                                    properties={'time_recorded': row['time_recorded']})
                    for row in rows if float(row['lat']) > 0]

        return SiriTrip(key=key, geojson_feature_collection=geojson.FeatureCollection(features))

        # %%


def groupby(iterable, projection):
    result = defaultdict(list)
    for item in iterable:
        result[projection(item)].append(item)
    return result


def read_siri_trips_from_exported_file(f):
    return [SiriTrip.of_csv_rows(siri_key, siri_csv_rows)
            for siri_key, siri_csv_rows
            in groupby(csv.DictReader(f), SiriKey.of_csv_row).items()]


# %% md
# GTFS Objects
# %%
# GTFS_STAT

class Route():
    def __init__(self, route_id, date, route_short_name, agency_name, stops,
                 route_long_name, is_loop, route_type, start_zone, end_zone,
                 service_duration, speed, start_times, trip_ids):
        self.route_id = route_id
        self.date = date
        self.route_short_name = route_short_name
        self.agency_name = agency_name
        self.stops = stops
        self.route_long_name = route_long_name
        self.is_loop = is_loop
        self.route_type = route_type
        self.start_zone = start_zone
        self.end_zone = end_zone
        self.service_duration = service_duration
        self.speed = speed
        self.start_times = start_times
        self.trip_ids = trip_ids

    def __repr__(self):
        return "Route: " + "@".join([self.route_id, self.date, self.route_short_name, self.agency_name])

    @staticmethod
    def parse(csv_row):
        stops = [geojson.Feature(geometry=geojson.Point((float(itr[0][0]), float(itr[0][1]))),
                                 properties=dict(stop_code=itr[1],
                                                 stop_id=itr[2]))
                 for itr in zip([i.split(',') for i in csv_row['all_stop_latlon'].split(';')],
                                csv_row['all_stop_code'].split(';'), csv_row['all_stop_id'].split(';'))]

        return Route(route_id=csv_row['route_id'],
                     date=csv_row['date'],
                     route_short_name=csv_row['route_short_name'],
                     agency_name=csv_row['agency_name'],
                     stops=stops,
                     route_long_name=csv_row['route_long_name'],
                     is_loop=csv_row['is_loop'],
                     route_type=csv_row['route_type'],
                     start_zone=csv_row['start_zone'],
                     end_zone=csv_row['end_zone'],
                     service_duration=csv_row['service_duration'],
                     speed=csv_row['service_speed'],
                     start_times=csv_row['all_start_time'].split(';'),
                     trip_ids=csv_row['all_trip_id'].split(';'))
    # %% md


# Handle SHAPE FIle
# %%
# SHAPE

def create_line_string_from_shape_file(path):
    coordinates = [tuple([float(i['shape_pt_lat']), float(i['shape_pt_lon'])])
                   for i in csv.DictReader(open(path, encoding="utf8"))]

    return geojson.LineString(coordinates=coordinates)


# %% md
# Combine the data as one structure
# %%
siri_data = read_siri_trips_from_exported_file(open(SIRI_EXPORTED_FROM_SPLUNK, encoding="utf8"))
# %%
gtfs_stat_data = [Route.parse(row) for row in csv.DictReader(open(GTFS_STAT_EXPORTED_FROM_SPLUNK, encoding="utf8"))]
gtfs_stat_data_dict = {(i.date, i.route_id): i for i in gtfs_stat_data}
# %%
shape = create_line_string_from_shape_file(SHAPE_FILE_7716)
# %%
results = []

for siri_itm in filter(lambda x: x.key.route_id == '7716', siri_data):
    gtfs_itm = gtfs_stat_data_dict[(siri_itm.key.date, siri_itm.key.route_id)]
    curr_shape = shape

    tripId = None
    if siri_itm.key.planned_start_time in gtfs_itm.start_times:
        tripId = gtfs_itm.trip_ids[gtfs_itm.start_times.index(siri_itm.key.planned_start_time)]

    res = dict(tripId=tripId,
               planned_time=siri_itm.key.planned_start_time,
               date=gtfs_itm.date,
               routeId=gtfs_itm.route_id,
               routeShortName=gtfs_itm.route_short_name,
               routeLongName=gtfs_itm.route_long_name,
               agencyName=gtfs_itm.agency_name,
               routeType=gtfs_itm.route_type,
               stops=gtfs_itm.stops,
               startZone=gtfs_itm.start_zone,
               endZone=gtfs_itm.end_zone,
               isLoop=gtfs_itm.is_loop,
               distance=None,
               duration=gtfs_itm.service_duration,
               speed=gtfs_itm.speed,
               shape=curr_shape,
               siri=siri_itm.geojson_feature_collection)

    results.append(res)
# %%
json.dump(results, open('out', 'w', encoding="utf8"), ensure_ascii=False)
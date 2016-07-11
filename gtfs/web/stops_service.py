from gtfs.parser.gtfs_reader import GTFS
from gtfs.parser.route_stories import load_route_stories_from_csv
from gtfs.kavrazif.kavrazif import load_train_station_distance, routes_calling_at_stop, route_frequency
from collections import defaultdict

import falcon
from wsgiref import simple_server

from sklearn.neighbors import KDTree
import numpy as np
import os
import json
from datetime import date

gtfs_folder = 'data/gtfs/gtfs_2016_05_25/'
start_date = date(2016, 6, 1)



class IndexServer:
    def __init__(self):
        self.content = open(os.path.join(os.path.dirname(__file__), 'stops.html'), encoding='utf8').read()

    def on_get(self, req, resp):
        self.content = open(os.path.join(os.path.dirname(__file__), 'stops.html'), encoding='utf8').read()
        resp.body = self.content
        resp.set_header('Content-Type', 'text/html')


class StopFinder:
    def __init__(self):
        self.gtfs = GTFS(os.path.join(gtfs_folder, 'israel-public-transportation.zip'))
        self.gtfs.load_stops()
        self.gtfs.load_routes()

        print("Loading tree")
        stop_locations = np.matrix([(s.stop_lat, s.stop_lon) for s in self.gtfs.stops.values()])
        self.stops = [s for s in self.gtfs.stops.values()]
        self.tree = KDTree(stop_locations)
        print("Tree loaded")

        print("Loading station distance")
        self.station_distance = load_train_station_distance(gtfs_folder)
        print("Station distance loaded")

        print("Loading route stories")
        route_stories, trip_to_stories = load_route_stories_from_csv(os.path.join(gtfs_folder, 'route_stories.txt'),
                                                                     os.path.join(gtfs_folder,
                                                                                  'trip_to_stories.txt'))
        print("Route stories loaded")

        print("Loading routes calling at stops")
        route_freq = route_frequency(self.gtfs, start_date)
        self.routes_calling_at_stop = defaultdict(lambda: [])
        for stop_id, routes in routes_calling_at_stop(self.gtfs, trip_to_stories, start_date).items():
            self.routes_calling_at_stop[stop_id] = [(route, *route_freq[route]) for route in routes]
        print("Calling at stops loaded")
        print("Ready.")

    def find(self, lat, lng):
        d, p = self.tree.query(np.matrix((lat, lng)), k=1, return_distance=True)  # d[0] is the distance
        return self.stops[p[0]]

    def on_get(self, req, resp):
        """Handles GET requests"""
        lat = float(req.get_param('lat'))
        lng = float(req.get_param('lng'))
        print("Request received for (%s,%s)" % (lat, lng))
        # find nearest bus stop to click location
        stop = self.find(lat, lng)
        # nearest train station to the bus stop
        nearest_train_station = self.station_distance[stop.stop_id]
        train_station_name = self.gtfs.stops[nearest_train_station.station_id].stop_name
        train_station_distance = nearest_train_station.distance
        # routes stopping at the bus stop
        routes = [{
                      'line_number': route_and_frequency[0].line_number,
                      'route_code': route_and_frequency[0].route_desc,
                      'weekday_calls': route_and_frequency[1],
                      'weekend_calls': route_and_frequency[2]
                  } for route_and_frequency in self.routes_calling_at_stop[stop.stop_id]]

        resp.body = json.dumps({
            'stop_id': stop.stop_id,
            'stop_code': stop.stop_code,
            'stop_name': stop.stop_name,
            'stop_desc': stop.stop_desc,
            'zone_id': stop.zone_id,
            'lat': stop.stop_lat,
            'lng': stop.stop_lon,
            'is_train_station': train_station_distance == 0,
            'train_station': train_station_name,
            'train_station_distance': int(train_station_distance),
            'routes': routes
        })


app = falcon.API()
app.add_route('/', IndexServer())
app.add_route('/stop', StopFinder())

# Useful for debugging problems in your API; works with pdb.set_trace(). You
# can also use Gunicorn to host your app. Gunicorn can be configured to
# auto-restart workers when it detects a code change, and it also works
# with pdb.
if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()

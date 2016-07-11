from gtfs.parser.gtfs_reader import GTFS

import falcon
from wsgiref import simple_server

from sklearn.neighbors import KDTree
import numpy as np
import os
import json


class IndexServer:
    def __init__(self):
        self.content = open(os.path.join(os.path.dirname(__file__), 'stops.html'), encoding='utf8').read()

    def on_get(self, req, resp):
        resp.body = self.content
        resp.set_header('Content-Type', 'text/html')


class StopFinder:
    def __init__(self):
        gtfs = GTFS('data/gtfs/gtfs_2016_05_25/israel-public-transportation.zip')
        gtfs.load_stops()
        stop_locations = np.matrix([(s.stop_lat, s.stop_lon) for s in gtfs.stops.values()])
        self.stops = [s for s in gtfs.stops.values()]
        print("Loading tree")
        self.tree = KDTree(stop_locations)
        print("Tree loaded")

    def find(self, lat, lng, max_distance=1):
        d, p = self.tree.query(np.matrix((lat, lng)), k=1, return_distance=True)
        print(p, d)
        return self.stops[p[0]]

    def on_get(self, req, resp):
        """Handles GET requests"""
        lat = float(req.get_param('lat'))
        lng = float(req.get_param('lng'))
        print("Request received for (%s,%s)" % (lat, lng))
        stop = self.find(lat, lng)
        print("Reply: %s", stop.stop_id)
        resp.body = json.dumps({
            'stop_id':  stop.stop_id,
            'stop_code': stop.stop_code,
            'stop_name': stop.stop_name,
            'stop_desc': stop.stop_desc,
            'zone_id': stop.zone_id,
            'lat': stop.stop_lat,
            'lng': stop.stop_lon
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

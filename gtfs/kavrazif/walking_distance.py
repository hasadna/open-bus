import requests
import os
import json
from gtfs.kavrazif.geo import GeoPoint


def google_maps_navigation_query(start_point, end_point, api_key):
    params = {'origin': '%f,%f' % (start_point.lat, start_point.lon),
              'destination': '%f,%f' % (end_point.kat, end_point.lon),
              'key': api_key,
              'mode': 'walking',
              'language': 'en' }
    r = requests.get('https://maps.googleapis.com/maps/api/directions/json', params=params)
    return r.json()


def process_google_maps_reply(google_json):
    if google_json['status'] != 'OK':
        raise Exception('status is not OK, status=%s' % google_json['status'])
    route = google_json['routes'][0]
    leg = route['legs'][0]
    route_length = leg['distance']['value']
    # encoded_polyline = route['overview_polyline']['points']
    points_dicts = [leg["start_location"]] + [step["end_location"] for step in leg["steps"]]
    points = [GeoPoint(p['lat'], p['lng']) for p in points_dicts]
    return route_length, points


def graph_hopper_navigation_query(start_point, end_point, api_key):
    param_keys = ('point', 'point', 'vehicle', 'instructions', 'points_encoded', 'debug')
    param_values = ('?', '?', 'foot', 'false', 'false', 'true')
    r = requests.get('https://graphhopper.com/api/1/route', params=[param_keys, param_values])
    return r.json


def process_graph_hopper_reply(gh_json):
    path = gh_json['paths'][0]
    length = path['distance']
    points = [GeoPoint(p[1], p[0]) for p in path['points']['coordinates']]
    return length, points

if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), 'google_navigation_result.json'), 'r', encoding='utf8') as f:
        print(process_google_maps_reply(json.load(f)))
    with open(os.path.join(os.path.dirname(__file__), 'graphopper_navigation_result.json'), 'r', encoding='utf8') as f:
        print(process_graph_hopper_reply(json.load(f)))



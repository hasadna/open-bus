import requests
import os
import json
from gtfs.kavrazif.geo import GeoPoint
import sys


def google_maps_navigation_query(start_point, end_point, api_key):
    params = {'origin': '%f,%f' % (start_point.lat, start_point.long),
              'destination': '%f,%f' % (end_point.lat, end_point.long),
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
    params = {
        'point': ['%f,%f' % (start_point.lat, start_point.long),
                  '%f,%f' % (end_point.lat, end_point.long)],
        'vehicle': 'foot',
        'instructions': 'false',
        'points_encoded': 'false',
        'debug': 'true',
        'key': api_key
    }
    r = requests.get('https://graphhopper.com/api/1/route', params=params)
    print(r.url)
    return r.json()


def process_graph_hopper_reply(gh_json):
    path = gh_json['paths'][0]
    length = path['distance']
    points = [GeoPoint(p[1], p[0]) for p in path['points']['coordinates']]
    return length, points


if __name__ == '__main__':
    # supply graphhopper api_key as first parameter
    api_key = sys.argv[1]
    start_point = GeoPoint(32.103555,34.804705)
    end_point = GeoPoint(32.102613,34.805102)
    print(process_graph_hopper_reply(graph_hopper_navigation_query(start_point, end_point, api_key)))

    # supply google maps api key as second parameter
    print(process_google_maps_reply(google_maps_navigation_query(start_point, end_point, sys.argv[2])))
    
    with open(os.path.join(os.path.dirname(__file__), 'google_navigation_result.json'), 'r', encoding='utf8') as f:
        print(process_google_maps_reply(json.load(f)))
    with open(os.path.join(os.path.dirname(__file__), 'graphopper_navigation_result.json'), 'r', encoding='utf8') as f:
        print(process_graph_hopper_reply(json.load(f)))



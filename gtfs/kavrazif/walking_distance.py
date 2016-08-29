import csv
from argparse import ArgumentParser

import requests

from gtfs.kavrazif.geo import GeoPoint


def google_maps_navigation_query(start_point, end_point, api_key):
    params = {'origin': '%f,%f' % (start_point.lat, start_point.long),
              'destination': '%f,%f' % (end_point.lat, end_point.long),
              'key': api_key,
              'mode': 'walking',
              'language': 'en'}
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


def google(start_point, end_point, api_key):
    return process_google_maps_reply(google_maps_navigation_query(start_point, end_point, api_key))


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
    return r.json()


def process_graph_hopper_reply(gh_json):
    path = gh_json['paths'][0]
    length = path['distance']
    points = [GeoPoint(p[1], p[0]) for p in path['points']['coordinates']]
    return length, points


def gh(start_point, end_point, api_key):
    return process_graph_hopper_reply(graph_hopper_navigation_query(start_point, end_point, api_key))


def build_walking_distance_table(stops_file, stations_file, output_file, google_api_key, gh_api_key, max_distance=400):
    def format_path(list_of_points):
        return ' '.join('%f %f' % (point.lat, point.long) for point in list_of_points)

    # read stops data
    table = []
    with open(stops_file, "r", encoding='utf8') as f:
        reader = csv.DictReader(f)
        for data in reader:
            data['station_distance'] = float(data['station_distance'])
            if data['stop_id'] != data['station_id'] and data['station_distance'] <= max_distance:
                data['stop_point'] = GeoPoint(data['stop_lat'], data['stop_lon'])
                table.append(data)
    print("Read %d stops with straight_line distance <= %d" % (len(table), max_distance))

    # getting real coordinates for train stations
    station_real_location = {}
    with open(stations_file, "r", buffering=-1, encoding="utf8") as g:
        next(g)  # skip header
        for line in g:
            data = line.split(",")
            station_real_location[data[1]] = GeoPoint(float(data[3]), float(data[4]))

    headers = ["stop_id", "station_id", "stop_code", "station_code", "station_distance",
               "stop_lat", "stop_lon", "station_lat", "station_lon",
               'Google_walking_distance', 'GH_walking_distance', 'Google_directions', 'GH_directions']

    with open(output_file, 'w', newline='', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=headers, lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        for stop in table:
            stop['station_point'] = station_real_location[stop['station_code']]

            distance, points = google(stop['stop_point'], stop['station_point'], google_api_key)
            stop['Google_walking_distance'] = distance
            stop['Google_directions'] = format_path(points)

            distance, points = gh(stop['stop_point'], stop['station_point'], gh_api_key)
            stop['GH_walking_distance'] = distance
            stop['GH_directions'] = format_path(points)

            stop['station_lat'] = stop['station_point'].lat
            stop['station_lon'] = stop['station_point'].long
            writer.writerow(stop)
            f.flush()

  
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--google_api_key', dest='google_api_key')
    parser.add_argument('--gh_api_key', dest='gh_api_key')
    parser.add_argument('--stops_file', dest='stops_file')
    parser.add_argument('--stations_file', dest='stations_file')
    parser.add_argument('--output_file', dest='output_file')
    parser.add_argument('--max_distance', dest='max_distance', type=int,
                        help='Maximum straight line distance to include in results')
    args = parser.parse_args()
    build_walking_distance_table(stops_file=args.stops_file, stations_file=args.stations_file,
                                 gh_api_key=args.gh_api_key, google_api_key=args.google_api_key,
                                 output_file=args.output_file, max_distance=args.max_distance)

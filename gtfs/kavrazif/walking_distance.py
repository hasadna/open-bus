import csv
from argparse import ArgumentParser
from collections import defaultdict

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
        raise Exception('status is not OK, status=%s, json=%s' % (google_json['status'], google_json))
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
    if 'paths' not in gh_json:
        if 'message' in gh_json:
            raise Exception('error in gh query: %s' % gh_json['message'])
        else:
            raise Exception('Badly formatted json %s' % gh_json)
    path = gh_json['paths'][0]
    length = path['distance']
    points = [GeoPoint(p[1], p[0]) for p in path['points']['coordinates']]
    return length, points


def gh(start_point, end_point, api_key):
    return process_graph_hopper_reply(graph_hopper_navigation_query(start_point, end_point, api_key))


def build_walking_distance_table(stops_file, stations_file, output_file, google_api_key, gh_api_key, max_distance=400,
                                 simulate=False):
    def format_path(list_of_points):
        return ' '.join('%f %f' % (p.lat, p.long) for p in list_of_points)

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
    station_real_location = defaultdict(lambda: [])
    with open(stations_file, "r", buffering=-1, encoding="utf8") as g:
        reader = csv.DictReader(g)
        for line in reader:
            if line['Type'] == 'Entrance':  # we skip exits for now because they make things to complicated
                station_real_location[line['stop_code']].append(GeoPoint(float(line['latitude']),
                                                                         float(line['longitude'])))

    print("Read locations for %d train stations" % len(station_real_location))
    print("Stations with 1 entrance: %d" % len([l for l in station_real_location.values() if len(l) == 1]))
    print("Stations with 2 entrances: %d" % len([l for l in station_real_location.values() if len(l) == 2]))
    print("Stations more than 2 entrances: %d" % len([l for l in station_real_location.values() if len(l) > 2]))

    queries_required = sum(len(station_real_location[stop['station_code']]) for stop in table)
    print("Total number of queries required=%d" % queries_required)

    if simulate:
        return

    headers = ["stop_id", "station_id", "stop_code", "station_code", "station_distance",
               "stop_lat", "stop_lon",
               'google_walking_distance', 'gh_walking_distance',
               'google_station_lat', 'google_station_lon',
               'gh_station_lat', 'gh_station_lon',
               'google_directions', 'gh_directions']

    with open(output_file, 'w', newline='', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=headers, lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        for stop in table:
            # a station may have multiple entrances
            for point in station_real_location[stop['station_code']]:
                distance, points = google(stop['stop_point'], point, google_api_key)
                if distance < stop.get('google_walking_distance', 999999):
                    stop['google_walking_distance'] = distance
                    stop['google_directions'] = format_path(points)
                    stop['google_station_lat'], stop['google_station_lon'] = point.lat, point.long

                distance, points = gh(stop['stop_point'], point, gh_api_key)
                if distance < stop.get('gh_walking_distance', 999999):
                    stop['gh_walking_distance'] = distance
                    stop['gh_directions'] = format_path(points)
                    stop['gh_station_lat'], stop['gh_station_lon'] = point.lat, point.long

            writer.writerow(stop)
            f.flush()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--google_api_key', dest='google_api_key')
    parser.add_argument('--gh_api_key', dest='gh_api_key',
                        help="Graph Hopper API key")
    parser.add_argument('--stops_file', dest='stops_file')
    parser.add_argument('--stations_file', dest='stations_file')
    parser.add_argument('--output_file', dest='output_file')
    parser.add_argument('--max_distance', dest='max_distance', type=int,
                        help='Maximum straight line distance to include in results')
    parser.add_argument('--simulate', help="Print how many API queries are required; don't run any queries",
                        action='store_true')
    parser.set_defaults(simulate=False)

    args = parser.parse_args()
    build_walking_distance_table(stops_file=args.stops_file, stations_file=args.stations_file,
                                 gh_api_key=args.gh_api_key, google_api_key=args.google_api_key,
                                 output_file=args.output_file, max_distance=args.max_distance,
                                 simulate=args.simulate)

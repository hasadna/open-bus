import csv
from argparse import ArgumentParser
from collections import defaultdict, namedtuple

import requests
import datetime

from geo import GeoPoint


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
    route_length = round(leg['distance']['value'])
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
    length = round(path['distance'])
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
            data['station_distance'] = float(data['train_station_distance'])
            if data['stop_code'] != data['nearest_train_station'] and int(data['train_station_distance']) <= max_distance:
                data['stop_point'] = GeoPoint(data['stop_lat'], data['stop_lon'])
                table.append(data)
    print("Read %d stops with straight_line distance <= %d" % (len(table), max_distance))

    # getting real coordinates for train stations
    station_real_location = defaultdict(lambda: [])
    with open(stations_file, "r", buffering=-1, encoding="utf8") as g:
        reader = csv.DictReader(g)
        for line in reader:
            if line['exit_only'] == 'False':  # we skip exits for now because they make things to complicated
                station_real_location[line['stop_code']].append(GeoPoint(float(line['exit_lat']),
                                                                         float(line['exit_lon'])))

    print("Read locations for %d train stations" % len(station_real_location))
    print("Stations with 1 entrance: %d" % len([l for l in station_real_location.values() if len(l) == 1]))
    print("Stations with 2 entrances: %d" % len([l for l in station_real_location.values() if len(l) == 2]))
    print("Stations more than 2 entrances: %d" % len([l for l in station_real_location.values() if len(l) > 2]))

    queries_required = sum(len(station_real_location[stop['nearest_train_station']]) for stop in table)
    print("Total number of queries required=%d" % queries_required)

    if simulate:
        return

    # create station_walking_distance table
    headers = ['bus_stop_code', 'bus_stop_lat', 'bus_stop_lon', 'train_station_code', 'train_station_entrace_id',
               'train_station_lat', 'train_station_lon', 'distance_in_meters', 'distance_source',
               'distance_calcated_on','notes']

    with open(output_file, 'w', newline='', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=headers, lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        for stop in table:
            # change fields names to station_walking_distance names
            stop['bus_stop_code'] = stop['stop_code']
            stop['bus_stop_lat'] = stop['stop_lat']
            stop['bus_stop_lon'] = stop['stop_lon']
            stop['train_station_code'] = stop['nearest_train_station']
            stop['distance_calcated_on'] = datetime.datetime.now().strftime("%d/%m/%Y")

            # calculate with Google
            stop['distance_source'] = 'Google'
            # a station may have multiple entrances
            for point in station_real_location[stop['nearest_train_station']]:
                stop['train_station_lat'], stop['train_station_lon'] = point.lat, point.long
                distance, points = google(stop['stop_point'], point, google_api_key)
                if distance < stop.get('distance_in_meters', 999999):
                    stop['distance_in_meters'] = distance
                    stop['notes'] = format_path(points)
            writer.writerow(stop)

            # calculate with Graphopper
            stop['distance_source'] = 'Graphopper'
            for point in station_real_location[stop['nearest_train_station']]:
                stop['train_station_lat'], stop['train_station_lon'] = point.lat, point.long
                distance, points = gh(stop['stop_point'], point, gh_api_key)
                if distance < stop.get('distance_in_meters', 999999):
                    stop['distance_in_meters'] = distance
                    stop['notes'] = format_path(points)
            writer.writerow(stop)

            f.flush()


def load_walking_distance_table(filename):
    Record = namedtuple('Record', 'station_id straight_line_distance google_distance gh_distance')

    def make_record(r):
        return Record(int(r['station_id']), float(r['station_distance']), float(r['google_walking_distance']),
                      float(r['gh_walking_distance']))

    with open(filename, encoding='utf8') as f:
        reader = csv.DictReader(f)
        return {int(r['stop_id']): make_record(r) for r in reader}


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
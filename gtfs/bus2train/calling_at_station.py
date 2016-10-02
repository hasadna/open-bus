import argparse
from datetime import datetime

from gtfs.parser.gtfs_reader import GTFS
from gtfs.parser.route_stories import load_route_stories_from_csv
from gtfs.bus2train.walking_distance import load_walking_distance_table
import os
from collections import defaultdict
import csv

"""Script to export all trains and buses calling at train station, on a given date"""


def trains_calling_at_stations(g, trip_to_route_story, on_date):
    """Returns a map from stop_id to list of trains calling there on given date"""
    print("Running trains_calling_at_stations")
    stop_to_calling_trains = defaultdict(lambda: [])
    for trip in g.trips.values():
        if trip.route.train_route and trip.active_on_date(on_date):
            start_time, route_story = trip_to_route_story[trip.trip_id]
            for route_story_stop in route_story.stops:
                stop_code = g.stops[route_story_stop.stop_id].stop_code
                stop_to_calling_trains[route_story_stop.stop_id].append((route_story_stop.stop_id,
                                                                         stop_code,
                                                                         trip.route.line_number,
                                                                         trip.route.route_desc,
                                                                         trip.route.route_long_name,
                                                                         start_time + route_story_stop.arrival_offset,
                                                                         start_time + route_story_stop.departure_offset,
                                                                         route_story_stop.pickup_type,
                                                                         route_story_stop.drop_off_type))
    return stop_to_calling_trains


def buses_calling_at_stations(g, trip_to_route_story, train_station_stops, on_date):
    print("Running buses_calling_at_stations")
    stop_to_calling_buses = defaultdict(lambda: [])
    for trip in g.trips.values():
        if trip.route.bus_route and trip.active_on_date(on_date):
            start_time, route_story = trip_to_route_story[trip.trip_id]
            for route_story_stop in route_story.stops:
                if route_story_stop.stop_id in train_station_stops:
                    stop_station_record = train_station_stops[route_story_stop.stop_id]
                    if stop_station_record.straight_line_distance <= 300:
                        train_station_id = stop_station_record.station_id
                        stop_code = g.stops[route_story_stop.stop_id].stop_code
                        stop_to_calling_buses[train_station_id].append((route_story_stop.stop_id,
                                                                        stop_code,
                                                                        trip.route.line_number,
                                                                        trip.route.route_desc,
                                                                        trip.route.route_long_name,
                                                                        start_time + route_story_stop.arrival_offset,
                                                                        start_time + route_story_stop.departure_offset,
                                                                        route_story_stop.pickup_type,
                                                                        route_story_stop.drop_off_type,
                                                                        stop_station_record.straight_line_distance,
                                                                        stop_station_record.google_distance,
                                                                        stop_station_record.gh_distance
                                                                        ))
    return stop_to_calling_buses


def export_calling_at_station(gtfs, stop_to_calling_trains, output_folder):
    for stop_id, calling_trains in stop_to_calling_trains.items():
        filename = '%s - %s.csv' % (gtfs.stops[stop_id].stop_code, gtfs.stops[stop_id].stop_name)
        with open(os.path.join(output_folder, filename), 'w', encoding='utf8') as f:
            writer = csv.writer(f, lineterminator='\n')
            header = ['stop_id', 'stop_code', 'line_number', 'route_desc', 'route_long_name',
                      'arrival', 'departure', 'pickup', 'drop_off',
                      'stop_station_distance', 'google_walking_distance', 'gh_walking_distance']
            writer.writerow(header)
            for record in calling_trains:
                writer.writerow(record)


def main(gtfs_folder, walking_distance_file, output_folder, on_date):
    gtfs = GTFS(os.path.join(gtfs_folder, 'israel-public-transportation.zip'))
    gtfs.load_trips()
    gtfs.load_stops()
    _, trip_to_route_story = load_route_stories_from_csv(os.path.join(gtfs_folder, 'route_stories.txt'),
                                                         os.path.join(gtfs_folder, 'trip_to_stories.txt'))
    station_stops = load_walking_distance_table(walking_distance_file)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # print readme
    with open(os.path.join(output_folder, 'readme.txt'), 'w', encoding='utf8') as f:
        readme = ["Trains and buses calling at trains stations",
                  "Created using %s" % __file__,
                  "Date for data: %s\n" % on_date,
                  "GTFS data from: %s\n" % gtfs_folder,
                  "Walking distance file (for bus stops serving train stations: %s\n" % walking_distance_file,
                  "",
                  "Fields:",
                  "stop_id - MoT identifier of the bus stop or station. For trains, this is always the id " +
                  "of the station for buses it's the id of the bus stop",
                  "stop_code - another MoT identifier for the stop or station",
                  "line_number - for buses, line number presented to passengers (e.g. on bus signage)",
                  "route_desc - an MoT identifier of the bus or train route",
                  "route_long_name - the name of the route",
                  "arrival - time of arrival to station \ stop",
                  "departure - time of departure from station",
                  "pickup - 0 if pickup is allowed, 1 if it's a drop off only stop (yes, this is counter intuitive)",
                  "dropoff - 0 if dropoff is allowed, 1 if it's a pickup only stop (yes, this is counter intuitive)"
                  "stop_station_distance - staight line distance between the stop and the associated train station",
                  "google_walking_distance - walking distance to train station, calculated with google maps api"
                  "gh_walking_distance - walking distance to train station, calculated with graph hopper api "
                  ]

        f.write("\n".join(readme))

    trains_folder = os.path.join(output_folder, 'trains')
    if not os.path.exists(trains_folder):
        os.makedirs(trains_folder)

    stop_to_calling_trains = trains_calling_at_stations(gtfs, trip_to_route_story, on_date)
    export_calling_at_station(gtfs, stop_to_calling_trains, trains_folder)

    buses_folder = os.path.join(output_folder, 'buses')
    if not os.path.exists(buses_folder):
        os.makedirs(buses_folder)

    export_calling_at_station(gtfs, buses_calling_at_stations(gtfs, trip_to_route_story, station_stops, on_date),
                              buses_folder)


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gtfs_folder', required=True)
    parser.add_argument('--output_folder', required=True)
    parser.add_argument('-d', '--on_date', help='format YYYY-MM-DD', required=True, type=valid_date)
    parser.add_argument('--walking_distance_file', required=True)
    args = parser.parse_args()
    main(gtfs_folder=args.gtfs_folder, walking_distance_file=args.walking_distance_file,
         output_folder=args.output_folder, on_date=args.on_date)

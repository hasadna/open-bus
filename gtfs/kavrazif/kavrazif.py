import gtfs.kavrazif.geo as geo
from collections import namedtuple
from gtfs.parser.gtfs_reader import *
from gtfs.parser import route_stories
import os
import sys


StationAndDistance = namedtuple('StationAndDistance', 'station_id distance')


def stop_to_station_distance(gtfs, trip_to_route_story):
    """For each stop in the gtfs, find the nearest train station and the distance from it"""
    """Adds nearest train station, train station distance and lines numbers"""
    gtfs.load_stops()
    gtfs.load_trips()

    # find train stations
    print("Finding train stations")
    train_trips = (trip for trip in gtfs.trips.values() if trip.route.route_type == 2)
    train_route_stories = set(trip_to_route_story[trip.trip_id].route_story for trip in train_trips)
    train_stations = set()
    for route_story in train_route_stories:
        for trip_story_stop in route_story:
            train_stations.add(trip_story_stop.stop_id)
    print("%d train stations found" % len(train_stations))

    # transform to geo-point objects
    train_stations_stops = (stop for stop in gtfs.stops.values() if stop.stop_id in train_stations)
    train_station_points = [(stop.stop_id, geo.GeoPoint(stop.stop_lat, stop.stop_lon))
                            for stop in train_stations_stops]

    def find_nearest_station(stop):
        stop_point = geo.GeoPoint(stop.stop_lat, stop.stop_lon)
        distance_and_stop = {train_station_point.distance_to(stop_point): train_station for
                             train_station, train_station_point in train_station_points}
        min_distance = min(distance_and_stop)
        nearest_station = distance_and_stop[min_distance]
        return StationAndDistance(nearest_station, min_distance)

    return {stop.stop_id: find_nearest_station(stop) for stop in gtfs.stops.values()}


def export_stop_station_distance_to_csv(output_file, stop_station_distance):
    print("Exporting stop station distance")
    with open(output_file, 'w') as f:
        f.write("stop_id,nearest_train_station_id,train_station_distance\n")
        for stop_id, (station_id, station_distance) in stop_station_distance.items():
            f.write(','.join(str(x) for x in [stop_id, station_id, station_distance]) + '\n')
    print("Export done")


def generate_station_distance(gtfs_folder):
    if 'route_stories.txt' not in os.listdir(gtfs_folder):
        print('route_stories.txt file not available in gtfs folder, please generate route stories first')
        return
    gtfs = GTFS(os.path.join(gtfs_folder, 'israel-public-transportation.zip'))
    _, trip_to_route_story = route_stories.load_route_stories_from_csv(
        os.path.join(gtfs_folder, '../sample/route_stories.txt'),
        os.path.join(gtfs_folder, '../sample/trip_to_stories.txt'))
    station_distance = stop_to_station_distance(gtfs, trip_to_route_story)
    export_stop_station_distance_to_csv(os.path.join(gtfs_folder, 'stop_station_distance.txt'), station_distance)


if __name__ == '__main__':
    generate_station_distance(sys.argv[1])

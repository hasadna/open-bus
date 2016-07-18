import gtfs.kavrazif.geo as geo
from collections import namedtuple, defaultdict
from gtfs.parser.gtfs_reader import *
from gtfs.parser.route_stories import load_route_stories_from_csv
import os
import sys
from datetime import timedelta

StationAndDistance = namedtuple('StationAndDistance', 'station_id distance')

RouteAndFrequency = namedtuple('RouteAndFrequency', 'route weekdays_trips weekend_trips')

weekdays = {6, 0, 1, 2, 3}


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
        for route_story_stop in route_story.stops:
            train_stations.add(route_story_stop.stop_id)
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


def export_stop_station_distance_to_csv(gtfs, output_file, stop_station_distance):
    print("Exporting stop station distance")
    with open(output_file, 'w') as f:
        f.write("stop_id,station_id,stop_code,station_code,station_distance\n")
        for stop_id, (station_id, station_distance) in stop_station_distance.items():
            stop_code = gtfs.stops[stop_id].stop_code
            station_code = gtfs.stops[station_id].stop_code
            f.write(','.join(str(x) for x in [stop_id, station_id,
                                              stop_code, station_code,
                                              station_distance]) + '\n')
    print("Export done")


def generate_station_distance(gtfs_folder):
    if 'route_stories.txt' not in os.listdir(gtfs_folder):
        print('route_stories.txt file not available in gtfs folder, please generate route stories first')
        return
    gtfs = GTFS(os.path.join(gtfs_folder, 'israel-public-transportation.zip'))
    _, trip_to_route_story = load_route_stories_from_csv(os.path.join(gtfs_folder, 'route_stories.txt'),
                                                         os.path.join(gtfs_folder, 'trip_to_stories.txt'))
    station_distance = stop_to_station_distance(gtfs, trip_to_route_story)
    export_stop_station_distance_to_csv(gtfs, os.path.join(gtfs_folder, 'stop_station_distance.txt'), station_distance)


def load_train_station_distance(gtfs_folder):
    with open(os.path.join(gtfs_folder, 'stop_station_distance.txt'), encoding='utf8') as f:
        reader = csv.DictReader(f)
        return {int(row['stop_id']): StationAndDistance(int(row['station_id']), float(row['station_distance']))
                for row in reader}


def route_frequency(gtfs, start_date):
    """returns a map from route, to a tuple (int, int) - number of trips for route for weekdays and weekends"""
    end_date = start_date + timedelta(days=7)
    gtfs.load_trips()
    res = defaultdict(lambda: (0, 0))
    for trip in gtfs.trips.values():
        if trip.service.end_date < start_date or trip.service.start_date > end_date:  # future or past trip
            continue
        (weekday_trips, weekend_trips) = res[trip.route]
        weekday_trips += len(trip.service.days.intersection(weekdays))
        weekend_trips += len(trip.service.days.difference(weekdays))
        res[trip.route] = (weekday_trips, weekend_trips)
    return res


def route_story_to_route(gtfs, trip_to_route_stories, start_date):
    """Returns a dictionary from route_story to the corresponding route

    trip_to_route_stories: dictionary trip_id to a TripRouteStory, as returned by load_route_stories_from_csv
    """
    gtfs.load_trips()
    end_date = start_date + timedelta(days=7)
    trips = (trip for trip in gtfs.trips.values() if
             trip.service.end_date < start_date or trip.service.start_date > end_date)
    return {trip_to_route_stories[trip.trip_id].route_story: trip.route for trip in trips}


def routes_calling_at_stop(gtfs, trip_to_route_stories, start_date):
    """Returns a dictionary from a stop_id to a List[Route] containing all routes calling there"""
    def key(r):
        return ''.join(d for d in r.line_number if d.isdigit()), r.route_desc

    res = defaultdict(lambda: set())
    for route_story, route in route_story_to_route(gtfs, trip_to_route_stories, start_date).items():
        for stop in route_story.stops:
            res[stop.stop_id].add(route)

    return {stop_id: sorted(list(routes), key=key) for stop_id, routes in res.items()}


if __name__ == '__main__':
    generate_station_distance(sys.argv[1])

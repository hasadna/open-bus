from gtfs.parser.gtfs_reader import GTFS, Service
from gtfs.kavrazif.kavrazif import load_train_station_distance, weekdays
from gtfs.parser import route_stories
import datetime
import os
import csv
from collections import defaultdict, Counter

route_types = {0: 'LightRailway', 2: 'Train', 3: 'Bus', 4: 'SharedTaxi'}
day_names = 'sunday monday tuesday wednesday thursday friday saturday'.split()
weekday_names = day_names[:5]
weekend_days = {4, 5}


def format_time(t):
    return '%02d:%02d:%02d' % (t / 3600, t % 3600 / 60, t % 60)


def parse_time(t):
    hour, minute, second = [int(f) for f in t.split(':')]
    return hour * 3600 + minute * 60 + second


class StationAccessFinder:
    """
    ##  Goal

    We want to find
    1) which bus stops are linked to train station (from which stops you can arrive to stations)
    2) What's the travel time from the bus to the station


    ## Implementation

    __1__: find train station bus stops set

    This will be done for now based on straight-line distance.

    Result: set of stop_id objects for near station stops

    __2__: for every route story, find indexes of train station stops

    for each route story, list of stop_sequence values of train station stops. (that is index of train station in the
    list of stops).

    Each time a route passes by a station, only a single stop will count as a station stop.

    Result: dictionary route_story_id -> list of indexes.

    __3__: for each route story that calls at a station, find the time from each stop to the next station

    for each route story, given (1) all stops (2) station stops, calculate the time from the stop to the next train
    station after it.

    Result: dictionary route_story_id -> list of (stop_id, station_id, time_to_station)

    __4__: calculate route story frequencies

    done by iterating over trips, similar to current ```route_frequency``` function.

    Result: dictionary route_story_id -> (weekday_frequency, weekend_frequency)

    __5__: load route to route story dictionary

    Result: dictionary route_story_id -> route object

    __6__: aggregate by route

    Route frequency = sum(route_story.frequency for route_story in route.route_stories)

    for each route + stop_id + station_d, calculate time_to_station as weighted average of time_to_station of each
    relevant route story (weighted by route_story frequency)

    Result: list of ```route_id,stop_id,station_id,time_to_station,frequency``` tuples

    __7__: aggregate by stop

    stop.routes = list of route_id for routes that call at stop
    stop.frequency = sum(route.frequency for route in stop.routes)
    stop.time_to_station = sum(route.frequency * route.time_to_station for route in stop.routes) / stop.frequency

    Result:  stop_id,station_id,time_to_station,routes

    (final result, should be dumped)

    # todo:
    # * export stops_near_stations, extended_routes
    # * Extend to support bus trips from station
    # * Better ways to calculate "station stops" (manually using local knowledge? using Google walking directions API?)


    """

    class HasFrequency:
        def __init__(self):
            self.weekday_trips = 0
            self.weekend_trips = 0

        @property
        def total_trips(self):
            return self.weekday_trips + self.weekend_trips

        def add_trip_counts(self, other):
            self.weekday_trips += other.weekday_trips
            self.weekend_trips += other.weekend_trips

    class ExtendedRouteStory(HasFrequency):
        def __init__(self, route_story, station_stops):
            super().__init__()
            self.route_story = route_story
            self.station_stops = station_stops  # stage 2
            self.stop_and_station = []  # stage 3
            self.route = None

    class ExtendedRoute(HasFrequency):
        def __init__(self, route):
            super().__init__()
            self.route = route
            self.stops_to_station_to_travel_time = defaultdict(lambda: 0)

    class StopAndStation(HasFrequency):
        def __init__(self, stop_id, station_id):
            super().__init__()
            self.stop_id = stop_id
            self.station_id = station_id
            self.routes = []
            self.travel_time = 0

    def __init__(self, gtfs_folder, output_folder, start_date, end_date=None, station_stop_distance=300):
        print("StationAccessFinder.__init__")
        self.gtfs = GTFS(os.path.join(gtfs_folder, 'israel-public-transportation.zip'))
        self.gtfs_folder = gtfs_folder
        self.output_folder = output_folder
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        # load route stories
        print("Loading route stories")
        self.route_stories, self.trips_to_route_stories = route_stories.load_route_stories_from_csv(
            os.path.join(gtfs_folder, 'route_stories.txt'),
            os.path.join(gtfs_folder, 'trip_to_stories.txt'))
        print("   There are %d route stories" % len(self.route_stories))
        # configuration
        self.station_stop_distance = station_stop_distance
        self.start_date = start_date
        self.end_date = end_date if end_date is not None else start_date + datetime.timedelta(days=7)
        # things that will be build during run()
        self.stops_near_stations = None  # dictionary from stop_id to StopAndDistance object
        self.extended_route_stories = None
        self.extended_routes = None
        self.stop_and_stations = None

    def run_station_access(self):
        # stage 1
        self.find_station_stops()
        # stage 2
        self.route_story_train_station_stops()
        # stage 3
        self.route_story_stops_to_stations()
        # stage 4
        self.route_story_frequency()
        # stage 5
        self.route_story_to_route()
        # stage 6
        self.route_stops_and_stations()
        # stage 7
        self.aggregate_by_stop()
        self.export_stop_and_station()
        self.export_readme()

    def export_readme(self):
        with open(os.path.join(self.output_folder, 'readme.txt'), 'w', encoding='utf8') as f:
            f.write("Results of StationAccessFinder\n")
            f.write("Time of execution: %s\n" % datetime.datetime.now())
            f.write("Execution parameters:\n")
            f.write("  gtfs_folder: %s\n" % self.gtfs_folder)
            f.write("  start_date: %s\n" % self.start_date)
            f.write(
                "  bus stop is considered to be serving a train station if it's up to %dm from it (straight line)" %
                self.station_stop_distance)
            f.write('\n\n')
            f.write("Results:\n")
            f.write("  number of bus stops near stations: %d\n" % len(self.stops_near_stations))
            f.write("  number of bus routes calling at stations: %d\n" % len(self.extended_routes))

    def find_station_stops(self, include_trains=False):
        print("Running stage 1: find_station_stops")
        station_distance = load_train_station_distance(self.gtfs_folder)
        near_stations = ((stop_id, station_and_distance) for (stop_id, station_and_distance) in station_distance.items()
                         if station_and_distance.distance < self.station_stop_distance)
        if not include_trains:
            near_stations = ((stop_id, station_and_distance) for (stop_id, station_and_distance) in near_stations
                             if stop_id != station_and_distance.station_id)
        self.stops_near_stations = {stop_id: station_and_distance for (stop_id, station_and_distance) in near_stations}
        print("  %d stops near train stations" % len(self.stops_near_stations))

    def route_story_train_station_stops(self):
        print("Running stage 2: route_story_train_station_stops")
        # route story and all the stops near train stations
        route_story_and_stations = ((route_story,
                                     [stop for stop in route_story.stops if stop.stop_id in self.stops_near_stations])
                                    for route_story in self.route_stories.values())
        # filter only route stories calling at a train station, and create an ExtendedRouteStory object
        extended_route_stories = (self.ExtendedRouteStory(route_story, stops) for (route_story, stops) in
                                  route_story_and_stations if len(stops) > 0)
        # create a dictionary
        self.extended_route_stories = {extended_route_story.route_story.route_story_id: extended_route_story
                                       for extended_route_story in extended_route_stories}
        print("   There %d route_stories calling at train stations" % len(self.extended_route_stories))

    def route_story_stops_to_stations(self):
        print("Running stage 3: route_story_stops_to_stations")
        for extended_route_story in self.extended_route_stories.values():
            station_stops_iter = iter(extended_route_story.station_stops)
            next_station = next(station_stops_iter)
            for route_story_stop in extended_route_story.route_story.stops:
                if route_story_stop.stop_sequence > next_station.stop_sequence:
                    next_station = next(station_stops_iter, None)
                    if next_station is None:
                        break
                assert next_station.arrival_offset >= route_story_stop.arrival_offset, 'sort problem!'
                extended_route_story.stop_and_station.append((route_story_stop, next_station))

    def route_story_frequency(self):
        print("Running stage 4: route_story_frequency")
        self.gtfs.load_trips()
        trips = (trip for trip in self.gtfs.trips.values() if
                 trip.service.end_date >= self.start_date or trip.service.start_date <= self.end_date)
        for trip in trips:
            route_story_id = self.trips_to_route_stories[trip.trip_id].route_story.route_story_id
            if route_story_id in self.extended_route_stories:
                extended_route_story = self.extended_route_stories[route_story_id]
                for d in self.date_range():
                    if d.weekday() in weekdays:
                        extended_route_story.weekday_trips += 1
                    else:
                        extended_route_story.weekend_trips += 1

    def route_story_to_route(self):
        print("Running stage 5: route_story_to_route")
        for trip in self.gtfs.trips.values():
            route_story_id = self.trips_to_route_stories[trip.trip_id].route_story.route_story_id
            if route_story_id in self.extended_route_stories:
                self.extended_route_stories[route_story_id].route = trip.route

    def route_stops_and_stations(self):
        print("Running stage 6: route_stops_and_stations")
        self.extended_routes = {}
        for route_story in self.extended_route_stories.values():
            extended_route = self.extended_routes.setdefault(route_story.route.route_id,
                                                             self.ExtendedRoute(route_story.route))
            extended_route.add_trip_counts(route_story)
            for route_story_stop, route_story_station in route_story.stop_and_station:
                station_id = self.stops_near_stations[route_story_station.stop_id].station_id
                key = (route_story_stop.stop_id, station_id)
                travel_time = route_story_station.arrival_offset - route_story_stop.arrival_offset
                extended_route.stops_to_station_to_travel_time[key] += route_story.total_trips * travel_time

        for route in self.extended_routes.values():
            for k in route.stops_to_station_to_travel_time:
                route.stops_to_station_to_travel_time[k] /= route.total_trips

    def aggregate_by_stop(self):
        print("Running stage 7: aggregate_by_stop")
        self.stop_and_stations = {}
        for extended_route in self.extended_routes.values():
            for (stop_id, station_id), travel_time in extended_route.stops_to_station_to_travel_time.items():
                stop_and_station = self.stop_and_stations.setdefault((stop_id, station_id),
                                                                     self.StopAndStation(stop_id, station_id))
                stop_and_station.routes.append(extended_route.route)
                stop_and_station.add_trip_counts(extended_route)
                stop_and_station.travel_time += travel_time * extended_route.total_trips

        for stop_and_station in self.stop_and_stations.values():
            stop_and_station.travel_time /= stop_and_station.total_trips
        print("   %d (stop, station) pairs found" % len(self.stop_and_stations))

    def export_stop_and_station(self):
        print("Running export_stop_and_station")
        self.gtfs.load_stops()
        with open(os.path.join(self.output_folder, 'station_access.txt'), 'w', encoding='utf8') as f:
            writer = csv.DictWriter(f, lineterminator='\n',
                                    fieldnames=['stop_id', 'station_id', 'travel_time', 'weekday_trips',
                                                'weekend_trips', 'latitude', 'longitude', 'station_name',
                                                'line_numbers', 'route_ids', 'parent_stop'])
            writer.writeheader()
            for stop_and_station in self.stop_and_stations.values():
                writer.writerow({
                    'stop_id': stop_and_station.stop_id,
                    'station_id': stop_and_station.station_id,
                    'travel_time': int(stop_and_station.travel_time // 60),
                    'weekday_trips': stop_and_station.weekday_trips,
                    'weekend_trips': stop_and_station.weekend_trips,
                    'line_numbers': ' '.join(sorted(set(route.line_number for route in stop_and_station.routes))),
                    'route_ids': ' '.join(str(route.route_id) for route in stop_and_station.routes),
                    'latitude': self.gtfs.stops[stop_and_station.stop_id].stop_lat,
                    'longitude': self.gtfs.stops[stop_and_station.stop_id].stop_lon,
                    'station_name': self.gtfs.stops[stop_and_station.station_id].stop_name,
                    'parent_stop': self.gtfs.stops[stop_and_station.stop_id].parent_station
                })

    def date_range(self):
        d = self.start_date
        while d <= self.end_date:
            yield d
            d += datetime.timedelta(days=1)


class CallingAtStation:
    """
    Goal:
    1) Find all bus calls at stations
    2) Find all train calls at stations
    (these two can be exported as a basis for calculating wait times)
    3) Export hourly bus and train calls, and ratios, into an excel file

    How to:
    1) Find all stops near stations and all stations (use StationAccessFinder.find_station_stops)
    2) For each route story, list the RouteStoryStops that are in \ near stations
       (use StationAccessFinder.route_story_train_station_stops)
    3) Filter distinct stops
       The problem is that a bus can have multiple stops within walking distance of one station
       (for example slightly before the station and slightly after the station)
       On the other hand, circular routes can legitimately stop in one station more than once.
       So the logic is: for a stretch of stops up to m minutes from each other, take only the nearest stop
       if there are multiple calls at the same stations more then m minutes apart, take them all.
    4) Iterate trips and generate:
        (trip,stop,arrival_offset)
    5.2) Count the number of calls (both train and buses) for each hour of the day for each day of week
        Result: dictionary[station_id -> dictionary[(day, hour, route_type)->count]]
    5.1) Aggregate average weekday calls per hour
        Result: dictionary[station_id --> dictionary[(hour, route_type)->count]]
    6) Export the output of (4):
        route_id,route_desc,line_number,stop_id,stop_code,station_id,station_distance,station_name,
        service_id,start_date,end_date,days,route_type
    7) export the output of (5.2)

    """

    station_calls_fields = ['trip_id', 'route_id', 'route_code', 'route_direction', 'route_alternative', 'line_number',
                            'stop_id', 'stop_sequence',
                            'stop_code', 'station_id', 'station_code', 'station_distance', 'station_name', 'service_id',
                            'start_date', 'end_date', 'route_type', 'arrival_time', 'weekday_calls',
                            'weekend_calls'] + day_names

    def __init__(self, gtfs_folder, output_folder, start_date, end_date=None, max_station_distance=300,
                 minutes_between_distinct_calls=15):
        self.finder = StationAccessFinder(gtfs_folder, output_folder, start_date, end_date, max_station_distance)
        self.seconds_between_distinct_calls = minutes_between_distinct_calls * 60
        self.filtered_calls = []
        self.trips_and_stops = []
        self.hourly_calls = None
        self.hourly_calls_weekday_average = None

    def run_calling_at_station(self):
        # step 1
        self.finder.find_station_stops(include_trains=True)
        # step 2
        self.finder.route_story_train_station_stops()
        # step 3
        self.filter_distinct_stops()
        # step 4
        self.load_trips_and_stops()
        # step 5
        self.days_station_calls_counter()
        self.average_station_calls_counter()
        # step 6
        self.export_all_station_calls()
        # step 7
        self.export_average_hourly_calls()

    def filter_distinct_stops(self):
        print("3. filter_distinct_stops")
        for route_story in self.finder.extended_route_stories.values():
            filtered = [route_story.station_stops[0]]
            for route_story_stop in route_story.station_stops[1:]:
                curr_station = self.finder.stops_near_stations[route_story_stop.stop_id].station_id
                prev_station = self.finder.stops_near_stations[filtered[-1].stop_id].station_id
                if curr_station != prev_station:
                    filtered.append(route_story_stop)
                elif route_story_stop.arrival_offset - filtered[-1].arrival_offset > self.seconds_between_distinct_calls:
                    filtered.append(route_story_stop)
                else:
                    curr_distance = self.finder.stops_near_stations[route_story_stop.stop_id].distance
                    prev_distance = self.finder.stops_near_stations[filtered[-1].stop_id].distance
                    if curr_distance < prev_distance:
                        filtered = filtered[:-1] + [route_story_stop]
                    else:
                        self.filtered_calls.append([(route_story, route_story_stop, filtered[-1])])  # for debug prints
            route_story.station_stops = filtered

    def load_trips_and_stops(self):
        print("4. load_trips_and_stops ")
        self.finder.gtfs.load_trips()
        for trip in self.finder.gtfs.trips.values():
            route_story_id = self.finder.trips_to_route_stories[trip.trip_id].route_story.route_story_id
            if route_story_id in self.finder.extended_route_stories:
                for route_story_stop in self.finder.extended_route_stories[route_story_id].station_stops:
                    self.trips_and_stops.append((trip, route_story_stop))

    def export_all_station_calls(self):
        print("6. export_all_station_calls")
        self.finder.gtfs.load_stops()
        with open(os.path.join(self.finder.output_folder, 'station_calls.txt'), 'w', encoding='utf8') as f:
            w = csv.DictWriter(f, lineterminator='\n', fieldnames=self.station_calls_fields)
            w.writeheader()
            for trip, route_story_stop in self.trips_and_stops:
                stop_id, arrival_offset = route_story_stop.stop_id, route_story_stop.arrival_offset
                arrival_time = self.finder.trips_to_route_stories[trip.trip_id].start_time + arrival_offset
                route_code, route_direction, route_alternative = trip.route.route_desc.split('-')
                station_id = self.finder.stops_near_stations[stop_id].station_id
                row = {'trip_id': trip.trip_id,
                       'route_id': trip.route.route_id,
                       'route_code': route_code,
                       'route_direction': route_direction,
                       'route_alternative': route_alternative,
                       'line_number': trip.route.line_number,
                       'stop_id': stop_id,
                       'stop_code': self.finder.gtfs.stops[stop_id].stop_code,
                       'stop_sequence': route_story_stop.stop_sequence,
                       'station_id': station_id,
                       'station_code': self.finder.gtfs.stops[station_id].stop_code,
                       'station_name': self.finder.gtfs.stops[station_id].stop_name,
                       'station_distance': self.finder.stops_near_stations[stop_id].distance,
                       'service_id': trip.service.service_id,
                       'start_date': trip.service.start_date,
                       'end_date': trip.service.end_date,
                       'route_type': trip.route.route_type,
                       'arrival_time': format_time(arrival_time),
                       'weekday_calls': len(trip.service.days.difference(weekend_days)),
                       'weekend_calls': len(trip.service.days.intersection(weekend_days))}
                row.update({name: Service.weekday_names[name] in trip.service.days for name in day_names})
                w.writerow(row)

    def days_station_calls_counter(self):
        def get_hour(t):
            return t // 3600

        print("5.1 days_station_calls_counter")
        self.hourly_calls = defaultdict(lambda: Counter())
        for trip, route_story_stop in self.trips_and_stops:
            service = trip.service
            stop_id, arrival_offset = route_story_stop.stop_id, route_story_stop.arrival_offset
            for d in self.finder.date_range():
                day = d.weekday()
                if service.start_date <= d <= service.end_date and day in service.days:
                    station_id = self.finder.stops_near_stations[stop_id].station_id
                    hour = get_hour(self.finder.trips_to_route_stories[trip.trip_id].start_time + arrival_offset)
                    route_type = trip.route.route_type
                    self.hourly_calls[station_id][(day, hour, route_type)] += 1
        print("  There are results for %d stations" % len(self.hourly_calls))

    def average_station_calls_counter(self):
        print("5.2 average_station_calls_counter")
        self.hourly_calls_weekday_average = defaultdict(lambda: Counter())
        for station_id in self.hourly_calls:
            for (day, hour, route_type), count in self.hourly_calls[station_id].items():
                if day in weekdays:
                    self.hourly_calls_weekday_average[station_id][(hour, route_type)] += count

        n_days = len([x for x in self.finder.date_range() if x.weekday() in weekdays])
        print("  There are %d weekdays in period" % n_days)
        for station_id in self.hourly_calls_weekday_average:
            for key in self.hourly_calls_weekday_average[station_id]:
                self.hourly_calls_weekday_average[station_id][key] /= n_days

    def export_average_hourly_calls(self):
        def export(filename, route_type):
            print("export_average_hourly_calls with type %s" % route_type)
            with open(os.path.join(self.finder.output_folder, filename), 'w', encoding='utf8') as f:
                fields = ['station_id', 'station_code', 'station_name', 'daily_total']
                fields += ['h%02d' % hour for hour in range(26)]
                writer = csv.DictWriter(f, lineterminator='\n', fieldnames=fields)
                writer.writeheader()
                for station_id in self.hourly_calls_weekday_average:
                    row = {'station_id': station_id,
                           'station_code': self.finder.gtfs.stops[station_id].stop_code,
                           'station_name': self.finder.gtfs.stops[station_id].stop_name,
                           'daily_total': sum(self.hourly_calls_weekday_average[station_id][(hour, route_type)]
                                              for hour in range(26))}
                    row.update({'h%02d' % hour: self.hourly_calls_weekday_average[station_id][(hour, route_type)]
                                for hour in range(26)})
                    writer.writerow(row)

        self.finder.gtfs.load_stops()
        export('station_calls_stats_bus.txt', 3)
        export('station_calls_stats_train.txt', 2)

    @staticmethod
    def explode_stop_data(folder, weekdays_only=True, route_type=3):
        # read the data written by export_all_station_calls
        output_folder = os.path.join(folder, 'stations_%s' % route_types[route_type])
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        with open(os.path.join(folder, 'station_calls.txt'), 'r', encoding='utf') as f:
            reader = csv.DictReader(f)
            by_station = defaultdict(lambda: [])
            bus_records = (record for record in reader if record['route_type'] == str(route_type) and
                           (int(record['weekday_calls']) > 0 or not weekdays_only))
            for record in bus_records:
                by_station[record['station_id']].append(record)

        for station_id, records in by_station.items():
            records.sort(key=lambda r: parse_time(record['arrival_time']))
            station_name = records[0]['station_name']
            with open(os.path.join(output_folder, 'station_calls_%s.txt' % station_name), 'w', encoding='utf8') as f:
                w = csv.DictWriter(f, lineterminator='\n', fieldnames=CallingAtStation.station_calls_fields)
                w.writeheader()
                w.writerows(records)


def filter_station_access_results(folder, output_filename=None,
                                  max_time_difference_from_station=-1, stations_to_include=None,
                                  stations_to_exclude=None, only_nearest_station=False,
                                  min_weekday_trips=0):
    print("Running filter_station_access_results")
    if output_filename is None:
        output_filename = 'filtered_station_access_%s.txt' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # read original records and filter them
    with open(os.path.join(folder, 'station_access.txt'), 'r', encoding='utf8') as f:
        reader = csv.DictReader(f)
        records = [r for r in reader]
        original_counter = len(records)
        # filter max_time_difference_from_station
        if max_time_difference_from_station != -1:
            records = (r for r in records if int(r['travel_time']) <= max_time_difference_from_station)
        if stations_to_include:
            records = (r for r in records if int(r['station_id']) in stations_to_include)
        if stations_to_exclude:
            records = (r for r in records if int(r['station_id']) not in stations_to_exclude)
        if only_nearest_station:
            stop_to_record = {}
            for r in records:
                stop_id = r['stop_id']
                if stop_id not in stop_to_record or int(r['travel_time']) < int(stop_to_record[stop_id]['travel_time']):
                    stop_to_record[stop_id] = r
            records = stop_to_record.values()
        records = (r for r in records if int(r['weekday_trips']) >= min_weekday_trips)
    records = list(records)
    filtered_counter = len(records)

    with open(os.path.join(folder, output_filename), 'w', encoding='utf8') as w:
        writer = csv.DictWriter(w, fieldnames=reader.fieldnames, lineterminator='\n')
        writer.writeheader()
        writer.writerows(r for r in records)

    # document output
    readme_filename = os.path.splitext(output_filename)[0] + ".readme.txt"
    with open(os.path.join(folder, readme_filename), 'w', encoding='utf8') as f:
        f.write("Results of filter_station_access_results\n")
        f.write('input_file=%s\n' % os.path.join(folder, 'stops_and_stations.txt'))
        f.write('max_time_difference_from_station=%d\n' % max_time_difference_from_station)
        f.write('stations_to_include=%s\n' % stations_to_include)
        f.write('stations_to_exclude=%s\n' % stations_to_exclude)
        f.write('only_nearest_station=%s\n' % only_nearest_station)
        f.write('min_weekday_trips=%d\n' % min_weekday_trips)
        f.write('Number of original records=%d\n' % original_counter)
        f.write('Number of records after filter=%d\n' % filtered_counter)
    print("Done.")


if __name__ == '__main__':
    gtfs_folder = '../openbus_data/gtfs_2016_05_25'
    # output_folder = 'train_access_map'
    # finder = StationAccessFinder(gtfs_folder, output_folder, datetime.date(2016, 6, 1))
    # finder.run_station_access()
    # busiest_train_stations = {37358, 37312, 37350, 37388, 37292, 37376, 37378, 37318, 37386, 37380, 37348, 37360}
    # filter_station_access_results(output_folder, max_time_difference_from_station=30,
    #                               stations_to_exclude=busiest_train_stations, only_nearest_station=True,
    #                               min_weekday_trips=25)
    output_folder = 'train_access_stats'
    #finder = CallingAtStation(gtfs_folder, output_folder, datetime.date(2016, 6, 1), datetime.date(2016, 6, 14),
    #                          max_station_distance=300)
    #finder.run_calling_at_station()
    #CallingAtStation.explode_stop_data(output_folder)
    CallingAtStation.explode_stop_data(output_folder, route_type=3)
    CallingAtStation.explode_stop_data(output_folder, route_type=2)

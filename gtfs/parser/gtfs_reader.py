"""
A module for reading data from a GTFS zip file to memory.
"""
import zipfile
import datetime
import csv
import io
from typing import Dict, Optional


class GTFS:
    """
    A class that can read GTFS and contains all the GTFS data structures. Initialized with the GTFS zip file name.
    Creating the class doesn't load anything. Use load_all() to load all the data structures, or load just what you need
    using the individual load() functions
    """

    def __init__(self, filename):
        self.filename = filename
        self.agencies = None  # type: Optional[Dict[int, Agency]]
        self.routes = None  # type: Optional[Dict[int, Route]]
        self.shapes = None  # type: Optional[Dict[int, Shape]]
        self.services = None  # type: Optional[Dict[int, Service]]
        self.trips = None  # type: Optional[Dict[int, Trip]]
        self.stops = None  # type: Optional[Dict[int, Stop]]
        self.stop_times_loaded = False

    def load_all(self):
        self.load_routes()
        self.load_shapes()
        self.load_trips()
        self.load_stops()
        self.load_stop_times()

    def load_agencies(self):
        if self.agencies is None:
            with zipfile.ZipFile(self.filename) as z:
                print("Loading agencies")
                with z.open('agency.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf8'))
                    self.agencies = {agency.agency_id: agency for agency in
                                     (Agency.from_csv(record) for record in reader)}
                print("%d agencies loaded" % len(self.agencies))

    def load_routes(self):
        self.load_agencies()

        if self.routes is None:
            with zipfile.ZipFile(self.filename) as z:
                print("Loading routes")
                with z.open('routes.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf8'))
                    self.routes = {route.route_id: route for route in (Route.from_csv(record, self.agencies)
                                                                       for record in reader)}
                print("%d routes loaded" % len(self.routes))

    def load_shapes(self):
        if self.shapes is None:
            self.shapes = {}
            with zipfile.ZipFile(self.filename) as z:
                print("Loading shapes")
                with z.open('shapes.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf8'))
                    for record in reader:
                        Shape.from_csv(record, self.shapes)
                print("%d shapes loaded" % len(self.shapes))

    def load_services(self):
        if self.services is None:
            with zipfile.ZipFile(self.filename) as z:
                print("Loading services")
                with z.open('calendar.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf8'))
                    self.services = {service.service_id: service for service in
                                     (Service.from_csv(record) for record in reader)}
                print("%d services loaded" % len(self.services))

    def load_trips(self):
        self.load_services()
        self.load_routes()

        if self.trips is None:
            with zipfile.ZipFile(self.filename) as z:
                print("Loading trips")
                with z.open('trips.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf8'))
                    self.trips = {trip.trip_id: trip for trip in (Trip.from_csv(record,
                                                                                self.routes,
                                                                                self.services) for record in reader)}
                print("%d trips loaded" % len(self.trips))

    def load_stops(self):
        if self.stops is None:
            with zipfile.ZipFile(self.filename) as z:
                print("Loading stops")
                with z.open('stops.txt') as f:
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf8'))
                    self.stops = {stop.stop_id: stop for stop in (Stop.from_csv(record) for record in reader)}
                print("%d stops loaded" % len(self.stops))

    def load_stop_times(self):
        if not self.stop_times_loaded:
            self.load_trips()
            print("Loading stop times. This will be very slow.")
            with zipfile.ZipFile(self.filename) as z:
                print("Loading stop times")
                with z.open('stop_times.txt') as f:
                    print("  reading records from file")
                    records_by_trip_id = {}
                    for i, record in enumerate(csv.DictReader(io.TextIOWrapper(f, 'utf8'))):
                        records_by_trip_id.setdefault(record['trip_id'], []).append(StopTime.from_csv(record))
                        if i % 100000 == 0:
                            print(datetime.datetime.now())

                    print("  %d records read for %d trips" %
                          (sum(len(x) for x in records_by_trip_id.values()), len(records_by_trip_id)))

                    stop_times_to_trips = {}
                    for trip_id, records in records_by_trip_id.items():
                        records.sort(key=lambda stop_time: stop_time.stop_sequence)
                        if records[0].stop_sequence != 1 or records[-1].stop_sequence != len(records):
                            print("Bad stop time sequence %s" % records)
                            continue
                        stop_times_to_trips.setdefault(tuple(records), []).append(trip_id)
                    print("There are %d stop time sequences" % len(stop_times_to_trips))

                    for i, (stop_times, stop_time_trip_ids) in enumerate(stop_times_to_trips.items()):
                        for trip_id in stop_time_trip_ids:
                            self.trips[trip_id].stop_times = stop_times
            self.stop_times_loaded = True


class Agency:
    def __init__(self, agency_id, agency_name):
        self.agency_id = agency_id
        self.agency_name = agency_name

    @classmethod
    def from_csv(cls, csv_record):
        return cls(int(csv_record['agency_id']), csv_record['agency_name'])


class Route:
    # line number if called "route short name" in the gtfs
    def __init__(self, route_id, agency, line_number, route_long_name, route_desc, route_type):
        self.route_id = route_id
        self.agency = agency
        self.agency_id = agency.agency_id
        self.line_number = line_number
        self.route_long_name = route_long_name
        self.route_desc = route_desc
        self.route_type = route_type

    def __repr__(self):
        return "<Route %d>" % self.route_id

    def __eq__(self, other):
        return self.route_id == other.route_id

    def __hash__(self):
        return hash(self.route_id)

    @classmethod
    def from_csv(cls, csv_record, agencies):
        agency_id = int(csv_record['agency_id'])
        return cls(int(csv_record['route_id']),
                   agencies[agency_id],
                   csv_record['route_short_name'], csv_record['route_long_name'],
                   csv_record['route_desc'], int(csv_record['route_type']))


class Trip:
    def __init__(self, route, service, trip_id, direction_id, shape_id):
        self.route = route
        self.service = service
        self.trip_id = trip_id
        self.direction_id = direction_id
        self.shape_id = shape_id
        self.stop_times_ids = None
        self.stop_times = None

    @classmethod
    def from_csv(cls, csv_record, routes, services):
        route = routes[int(csv_record['route_id'])]
        service = services[int(csv_record['service_id'])]
        return cls(route,
                   service,
                   csv_record['trip_id'],
                   int(csv_record['direction_id']),
                   int(csv_record['shape_id']) if csv_record['shape_id'] != '' else -1)


class Service:
    weekday_names = dict(zip('monday tuesday wednesday thursday friday saturday sunday'.split(), range(7)))

    def __init__(self, service_id, days, start_date, end_date):
        self.end_date = end_date
        self.start_date = start_date
        self.days = days
        self.service_id = service_id

    def __eq__(self, other):
        return self.service_id == other.service_id

    def __hash__(self):
        return hash(self.service_id)

    @classmethod
    def from_csv(cls, csv_record):
        service_id = int(csv_record['service_id'])
        days = {Service.weekday_names[day] for day in Service.weekday_names.keys() if csv_record[day] == '1'}
        start_date = datetime.datetime.strptime(csv_record['start_date'], "%Y%m%d").date()
        end_date = datetime.datetime.strptime(csv_record['end_date'], "%Y%m%d").date()
        return cls(service_id, days, start_date, end_date)


class StopTime:
    # trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type
    def __init__(self, arrival_time, departure_time, stop_id, stop_sequence, pickup_type, drop_off_type):
        self.drop_off_type = drop_off_type
        self.pickup_type = pickup_type
        self.stop_sequence = stop_sequence
        self.stop_id = stop_id
        self.departure_time = departure_time
        self.arrival_time = arrival_time

    @classmethod
    def from_csv(cls, csv_record):
        def parse_timestamp(timestamp):
            """Returns second since start of day"""
            # We need to manually parse because there's hours >= 24; but ain't Python doing it beautifully?
            (hour, minute, second) = (int(f) for f in timestamp.split(':'))
            return hour * 60 * 60 + minute * 60 + second

        arrival_time = parse_timestamp(csv_record['arrival_time'])
        departure_time = parse_timestamp(csv_record['departure_time'])
        stop_id = int(csv_record['stop_id'])
        stop_sequence = int(csv_record['stop_sequence'])
        pickup_type = csv_record['pickup_type']
        drop_off_type = csv_record['drop_off_type']
        return cls(arrival_time, departure_time, stop_id, stop_sequence, pickup_type, drop_off_type)


class Stop:
    def __init__(self, stop_id, stop_code, stop_name, stop_desc, stop_lat, stop_lon, location_type, parent_station,
                 zone_id):
        self.stop_id = stop_id
        self.stop_code = stop_code
        self.stop_name = stop_name
        self.stop_desc = stop_desc
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon
        self.location_type = location_type
        self.parent_station = parent_station
        self.zone_id = zone_id

    def __eq__(self, other):
        return self.stop_id == other.stop_id

    def __hash__(self):
        return hash(self.stop_id)

    @property
    def town(self):
        return self.stop_desc.split(":")[2][:-5].strip()

    @classmethod
    def from_csv(cls, csv_record):
        stop_id = int(csv_record['stop_id'])
        field_names = "stop_code,stop_name,stop_desc,stop_lat,stop_lon,location_type,parent_station,zone_id".split(',')
        fields = [csv_record[field] for field in field_names]
        return cls(stop_id, *fields)


class Shape:
    def __init__(self, shape_id):
        self.shape_id = shape_id
        self.coordinates = {}

    def add_coordinate(self, point, sequence):
        self.coordinates[sequence] = point

    # shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence
    @classmethod
    def from_csv(cls, csv_record, current_shapes):
        shape_id = int(csv_record['shape_id'])
        point = (float(csv_record['shape_pt_lat']), float(csv_record['shape_pt_lon']))
        sequence = int(csv_record['shape_pt_sequence'])
        shape = current_shapes.setdefault(shape_id, Shape(shape_id))
        shape.add_coordinate(point, sequence)


if __name__ == '__main__':
    g = GTFS('../sample/israel-public-transportation.zip')
    g.load_all()

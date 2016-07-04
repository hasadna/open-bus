"""
Route stories: what they are and what they are good for

Background:
An intuitive model for a public transport would include the following objects:

* A bus line (e.g. bus line 189). In the GTFS this is called Route. The GTFS routes table has 
  separate records for each direction and alternative (halufa).
* A trip (e.g. 189 leaving terminal X on 2016-06-29 at 13:55). In practice most trips
  repeat every week or even every day. To reduce duplicates, a trip record in the GTFS doesn't 
  have a single date, but a start & end date and days of week.
* For each trip we would need the list of stops, and the arrival time to each stop. For example
  the Sunday 8:55 trip of 189, starts at stop X at time 8:55, arrive at stop Y at 8:56, arrives
  at stop z at 8:58 etc. This is implemented in the GTFS is stop_times table. 
  
What's the problem?
Since every trip has its own list of stops, the GTFS allow each trip of a route to be different.
So 189 of 8:55 could go from Tel-Aviv to Holon and 189 of 9:06 can go from Petah-Tikva to Azor.

In pracrice in Israel, each bus line has a fixed route (stop sequence). If a bus line has two 
routes (e.g. some trips go through a certain neighborhood and others don't) - the line will 
have to separate route records (halufot). The only reason for two different stop sequences
is if during the two months covered by the GTFS, there is a planned changed in the route
(so one stop sequence will be valid say until June 30th, and then a different starting July 1st).

And it gets better:

Not only the stop sequence is fixed, the arrival times to each stop are fixed. That is,
if the 08:00 trip arrives at stop x at 8:19, the 13:00 trip will arrive at stop x at 13:19.
There is not effort to publish (or probably even plan) a reasonable schedule that 
takes into account peak traffic.

Here comes in a new object, Route Story. A route story is a list of stops, and the time offset
of the arrival to the stop, compared to the beginning of the route.

E.g.:

    stop_times				route_story
    stop 1, 8:15			stop 1, 0
    stop 2, 8:27			stop 2, 12 minutes
    stop 3, 8:29			stop 3, 14 minutes
    ....					....

Every trip has a route story, and a start time:

    trip1:   stop 1, 8:15; stop 2, 8:27; stop 3, 8:29 ....
    trip2:   stop 1, 8:35; stop 2, 8:47; stop 3, 8:49 ....

becomes:
    route story 1:	stop 1, 0; stop 2, 12 minutes; stop 3, 14 minutes ...
    trip1: route_story 1, start_time  8:15
    trip2: route_story 2, start_time  8:35

Why is this good?
    - it saves a lot of space, and saves loading time if you need to analyse all the trips.
    - it makes logical sense, and makes it easy to examine the changes in route stories per route.

"""

import zipfile
import datetime
import csv
import io
from collections import defaultdict
import os
from gtfs_reader import GTFS, StopTime


class RouteStoryStop:
    def __init__(self, arrival_offset, departure_offset, stop_id, pickup_type, drop_off_type, stop_sequence=None):
        self.arrival_offset = arrival_offset
        self.departure_offset = departure_offset
        self.stop_id = stop_id
        self.pickup_type = pickup_type
        self.drop_off_type = drop_off_type
        self.stop_sequence = stop_sequence

    def __hash__(self):
        return hash(self.as_tuple())

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()

    def as_tuple(self):
        return self.arrival_offset, self.departure_offset, self.stop_id, self.pickup_type, self.drop_off_type

    def __str__(self):
        return 'stop_id=%s,stop_sequence=%s' % (self.stop_id, self.stop_sequence)

    def __repr__(self):
        return 'stop_id=%s,stop_sequence=%s' % (self.stop_id, self.stop_sequence)

    @classmethod
    def from_csv(cls, csv_record):
        route_story_id = int(csv_record['route_story_id'])
        field_names = "arrival_offset,departure_offset,stop_id,pickup_type,drop_off_type".split(',')
        fields = [csv_record[field] for field in field_names]
        fields = [int(field) if field != '' else 0 for field in fields]
        return route_story_id, cls(*fields)


class RouteStory:
    def __init__(self, route_story_id, stops):
        self.route_story_id = route_story_id
        self.stops = stops

    def __eq__(self, other):
        return self.route_story_id == other.route_story_id

    def __hash__(self):
        return hash(self.route_story_id)

    @classmethod
    def from_tuple(cls, route_story_id, route_story_stops):
        return RouteStory(route_story_id, route_story_stops)


def build_route_stories(gtfs: GTFS):
    """ Builds route stories. Returns a dictionary from id to RouteStory object, and a dictionary
    from trip to a tuple, (route_story_id, start_time)"""

    trip_id_to_stop_times_csv_records = defaultdict(lambda: [])

    def progenum(iterable, freq):
        """A primitive progress bar"""
        i = 0
        for i, r in enumerate(iterable):
            yield r
            if i % freq == 0:
                print("  ", i, datetime.datetime.now())
        print('Total number of iterations: %d' % i)

    def read_trip_id_to_stop_times():
        """Returns dictionary from trip_id to a list of csv records"""
        with zipfile.ZipFile(gtfs.filename) as z:
            with z.open('stop_times.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, 'utf8'))
                print("Reading stop_times file")
                for record in progenum(reader, 500000):
                    trip_id_to_stop_times_csv_records[record['trip_id']].append(record)
                print("Total number of trips in stop times file %d " % len(trip_id_to_stop_times_csv_records))

    def find_missing_trips():
        missing = [trip_id for trip_id in gtfs.trips if trip_id not in trip_id_to_stop_times_csv_records]
        if len(missing) > 0:
            print("%s trips have no route story" % len(missing))
            print("trips with no route stories are: %s" % missing)

    def sort_and_verify_csv_records():
        print("Sorting and verifying csv records")
        bad_trip_sequences = set()
        for trip_id, csv_records in progenum(trip_id_to_stop_times_csv_records.items(), 10000):
            csv_records.sort(key=lambda r: int(r['stop_sequence']))
            if csv_records[0]['stop_sequence'] != '1' or int(csv_records[-1]['stop_sequence']) != len(csv_records):
                bad_trip_sequences.add(trip_id)
        if len(bad_trip_sequences) > 0:
            print("There are %d trips with bad sequences of stops in route story" % len(bad_trip_sequences))
            for trip_id in bad_trip_sequences:
                print("  Trip %s, sequence %s" % (trip_id, trip_id_to_stop_times_csv_records[trip_id]))
                del (trip_id_to_stop_times_csv_records[trip_id])

    def build():
        route_story_to_id = {}  # Dict[int, RouteStory]
        trip_to_route_story = {}  # Dict[int, Tuple[int, datetime]]

        print("Building route stories")
        for trip_id, csv_records in progenum(trip_id_to_stop_times_csv_records.items(), 10000):
            # convert to ilgtfs.StopTime objects
            gtfs_stop_times = [StopTime.from_csv(record) for record in csv_records]
            # get the start time in seconds since the start of the day
            start_time = gtfs_stop_times[0].arrival_time
            # convert the StopTime object to RouteStoryStop object; use a tuple because it's hashable
            route_story_tuple = tuple(RouteStoryStop(record.arrival_time - start_time,
                                                     record.departure_time - start_time,
                                                     record.stop_id,
                                                     record.pickup_type,
                                                     record.drop_off_type) for record in gtfs_stop_times)
            # is it a new route story? if yes, allocate an id
            if route_story_tuple not in route_story_to_id:
                route_story_id = len(route_story_to_id) + 1
                route_story_to_id[route_story_tuple] = route_story_id
            trip_to_route_story[trip_id] = (route_story_to_id[route_story_tuple], csv_records[0]['departure_time'])

        # convert the route_story_tuples to RouteStory objects
        route_stories = {route_story_id: RouteStory.from_tuple(route_story_id, route_story_tuple)
                         for route_story_tuple, route_story_id in route_story_to_id.items()}
        print("Total number of route stories=%d" % len(route_stories))
        print("Total number of route story stops=%d" % sum(len(story.stops) for story in route_stories.values()))
        print("Done.")
        return route_stories, trip_to_route_story

    gtfs.load_routes()
    gtfs.load_trips()
    read_trip_id_to_stop_times()
    sort_and_verify_csv_records()  # sort the route stories by stop sequence, and make sure they are consistent
    find_missing_trips()  # this would just print the ids of trips without route story
    return build()


def export_route_stories_to_csv(output_file, route_stories):
    print("Exporting route story stops")
    with open(output_file, 'w') as f:
        f.write("route_story_id,arrival_offset,departure_offset,stop_id,stop_sequence,pickup_type,drop_off_type\n")
        for route_story_id, route_story in route_stories.items():
            for i, stop in enumerate(route_story.stops):
                f.write(','.join(str(x) for x in [route_story_id,
                                                  stop.arrival_offset,
                                                  stop.departure_offset,
                                                  stop.stop_id,
                                                  i + 1,
                                                  stop.pickup_type,
                                                  stop.drop_off_type]) + '\n')
    print("Route story export done")


def export_trip_route_stories_to_csv(output_file, trip_to_route_story):
    print("exporting %d full trips" % len(trip_to_route_story))
    with open(output_file, 'w') as f2:
        fields = ["trip_id", "start_time", "route_story"]
        writer = csv.DictWriter(f2, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for trip_id, (route_story_id, start_time) in trip_to_route_story.items():
            writer.writerow({"trip_id": trip_id,
                             "start_time": route_story_id,
                             "route_story": start_time})
    print("Trips export done.")


if __name__ == '__main__':
    gtfs_folder = r'../sample'
    g = GTFS('../sample/israel-public-transportation.zip')
    stories, trips = build_route_stories(g)
    export_route_stories_to_csv(os.path.join(gtfs_folder, 'route_stories.txt'), stories)
    export_trip_route_stories_to_csv(os.path.join(gtfs_folder, 'trip_to_stories.txt'), trips)

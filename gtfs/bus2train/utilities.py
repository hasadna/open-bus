import gtfs.bus2train.geo as geo
from collections import namedtuple, defaultdict
from gtfs.parser.gtfs_reader import *
from gtfs.parser.route_stories import load_route_stories_from_csv
import os
import sys
from datetime import timedelta

weekdays = {6, 0, 1, 2, 3}


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








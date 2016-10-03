"""
Interactive script to find a list a stop where a line is calling.
"""
import os
import sys
from collections import Counter
from argparse import ArgumentParser
import csv
from gtfs.parser.gtfs_reader import GTFS
from gtfs.parser.route_stories import load_route_stories_from_csv


def choose_route_by_line_number(line_number, g):
    candidates = set(r for r in g.routes.values() if r.line_number == line_number)
    route_trips_counter = Counter()
    for t in g.trips.values():
        if t.route in candidates:
            route_trips_counter[t.route] += 1

    candidates = list(sorted(candidates, key=lambda r: -1 * route_trips_counter[r]))

    print("Choose which route you want for line %s (type option number):" % line_number)
    print("Hint: if there are multiple options matching your preference, you probably want the one with more trips")
    for i, r in enumerate(candidates):
        print("Option %d" % (i + 1))
        print("==========")
        print("Route_id: %s" % r.route_id)
        print("Agency: %s" % r.agency.agency_name)
        (f, t) = r.route_long_name.split("<->")
        print("From: %s" % f.replace("''", '"'))
        print("To: %s" % t[:-3].replace("''", '"'))
        print("Number of trips: %d" % route_trips_counter[r])
        print()

    return candidates[int(input("Option number > ")) - 1]


def route_story_stops(route_story, gtfs):
    return [gtfs.stops[stop.stop_id] for stop in route_story.stops]


def route_stops(route, gtfs, trip_to_route_story):
    route_stories = {}
    for trip in gtfs.trips.values():
        if trip.route == route:
            route_story = trip_to_route_story[trip.trip_id].route_story
            dates = (trip.service.start_date, trip.service.end_date)
            route_stories[route_story] = dates

    if len(route_stories) == 0:
        raise Exception("No route stories found for route %s" % route)
    elif len(route_stories) == 1:
        return route_story_stops(list(route_stories.keys())[0], gtfs)
    else:
        stories_and_dates = list(sorted(route_stories.items(), key=lambda pair: pair[1]))
        print("This route has different stops on different dates. Choose which date range you want:")
        for i, (start_date, end_date) in enumerate(v[1] for v in stories_and_dates):
            print(" %d. from %s to %s" % (i + 1, start_date, end_date))
        print()
        choice = int(input("Option number > ")) - 1
        return route_story_stops(stories_and_dates[choice][0], gtfs)


def test_hebrew_console():
    try:
        print("מתחילים...")
    except UnicodeEncodeError:
        print("This script needs to print Hebrew to your console, and there's a problem with that.")
        print("If you are on Windows, you should install the win_unicode_console module")
        print("See https://github.com/daphshez/cheatsheets/blob/master/python/hebrew_in_win_console.md")
        sys.exit(-1)


def export_stops(stops, filename):
    print("Writing to output file %s" % filename)
    fieldnames = ['stop_id', 'stop_code', 'stop_name', 'town']
    with open(filename, 'w', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        for stop in stops:
            writer.writerow({
                'stop_id': stop.stop_id,
                'stop_code': stop.stop_code,
                'stop_name': stop.stop_name,
                'town': stop.town
            })


def main():
    test_hebrew_console()
    parser = ArgumentParser()
    parser.add_argument('--gtfs_folder', required=True)
    parser.add_argument('--line_number', required=True, type=str)
    parser.add_argument('--output_file', required=True)
    args = parser.parse_args()
    print("Loading gtfs, please wait...")
    g = GTFS(os.path.join(args.gtfs_folder, 'israel-public-transportation.zip'))
    g.load_routes()
    g.load_trips()
    g.load_stops()
    _, trip_to_route_story = load_route_stories_from_csv(os.path.join(args.gtfs_folder, 'route_stories.txt'),
                                                         os.path.join(args.gtfs_folder, 'trip_to_stories.txt'))
    route = choose_route_by_line_number(args.line_number, g)
    stops = route_stops(route, g, trip_to_route_story)
    export_stops(stops, args.output_file)
    print("Done.")


if __name__ == "__main__":
    main()

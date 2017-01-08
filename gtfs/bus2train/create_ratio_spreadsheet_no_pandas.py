"""
This is a clone of create_ratio_speadsheet that doesn't use pandas.

This Script is for making a spreadsheet for each day of ratio between buses and trains.
Three parameters are needed:
1. path to csv of all_buses (output of - postgres/bus2train/all_buses_near_train_stations.sql)
2. path to csv of all_trains (output of - postgres/bus2train/all_train_hours.sql)
3. path to csv of passengers average data (output of - http://data.obudget.org/queries/839)
3. output folder

please note the script is sensitive to the csv structure. So any change in query will result with fail of this script.

script also fixes bus and trains times as 25:00 and changes days accordingly"
"""

import argparse
import csv
from collections import Counter
import os
from gtfs.bus2train.gsheet_tools import csvs_to_gsheet, auto_fit_column_width
import datetime

WEEKDAYS = ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday')


def print_all_trips(filename, tbl, buses=False):
    fields = ["station_code", 'station_name', 'arrival_time', "hour", "direction_id"]
    if buses:
        fields += ['bus_route', 'bus_route_desc', 'bus_stop_name']
    tbl = sorted((r for r in tbl), key=lambda r: (r['station_name'], r['arrival_time']))
    with open(filename, 'w', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        for r in tbl:
            writer.writerow(r)


def output_pivot(filename, tbl, aggregates=[]):
    def prepare(x):
        return '' if x is None else ('%.2f' % x if type(x) == float else x)

    print("Writing", filename)
    with open(filename, 'w', encoding='utf8') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(["station"] + [str(h) for h in range(24)] + aggregates)
        for station in sorted(tbl):
            writer.writerow([station] + [prepare(tbl[station][h]) for h in range(24)] +
                            [prepare(tbl[station][a]) for a in aggregates])


def add_agg_row(tbl, agg_func, agg_name):
    for k in tbl:
        tbl[k][agg_name] = agg_func(tbl[k].values())


def calculate_ratio(tbl_a, tbl_b):
    """This function assumes to two tables have the same keys """
    return {k1: {k2: tbl_a[k1][k2] / tbl_b[k1][k2] if tbl_b[k1][k2] != 0 else None
                 for k2 in tbl_a[k1]}
            for k1 in tbl_a}


def create_pivot(tbl, all_stations):
    """Creates pivot for the buses and trains tables"""
    counter = Counter()
    for r in tbl:
        counter[(r['station_name'], r['hour'])] += 1
    return {station: {hour: counter.get((station, hour), 0) for hour in range(24)}
            for station in all_stations}


def create_pivot_passengers(tbl, all_stations):
    counter = Counter()
    summer = Counter()
    for r in tbl:
        counter[(r['station_name'], r['hour'])] += 1
        summer[(r['station_name'], r['hour'])] += r['avg']
    return {station: {hour: summer.get((station, hour), 0) / counter.get((station, hour), 1)
                      for hour in range(24)}
            for station in all_stations}


def load_data(tbl):
    with open(tbl, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f)
        return [r for r in reader]


def load_train_or_bus_data(file_name):
    tbl = load_data(file_name)
    tbl = rename_fields(tbl)
    tbl = apply_to_field(tbl, 'hour', lambda s: int(float(s)))
    for day in WEEKDAYS:
        tbl = apply_to_field(tbl, day, lambda b: b.lower() == "true")
    fix_times(tbl)
    return tbl


def load_passengers_data(file_name):
    tbl = load_data(file_name)
    tbl = rename_fields(tbl)
    tbl = apply_to_field(tbl, 'hour', lambda s: int(float(s)))
    tbl = apply_to_field(tbl, 'avg', lambda s: float(s) if s != '' else 0)
    return tbl


def rename_fields(tbl):
    old_to_new = {"stop_name": "station_name",
                  "stop_code": "station_code",
                  "train_time": "arrival_time",
                  "train_stop": "station_code",
                  "train_stop_name": "station_name",
                  "bus_time": "arrival_time"}
    old_to_new.update({"train_%s" % day: day for day in WEEKDAYS})
    old_to_new.update({"bus_%s" % day: day for day in WEEKDAYS})
    return [{old_to_new.get(k, k): v for (k, v) in row.items()} for row in tbl]


def apply_to_field(tbl, field_name, f):
    return [{k: f(v) if k == field_name else v for (k, v) in r.items()} for r in tbl]


def fix_times(tbl):
    counter = 0
    for r in tbl:
        if int(r["hour"]) >= 24:
            r["hour"] -= 24
            running_on_days = [r[day] for day in WEEKDAYS]
            running_on_days = [running_on_days[6]] + running_on_days[:6]
            for day, value in zip(WEEKDAYS, running_on_days):
                r[day] = value
            counter += 1
    print("Times fixed on %d trips" % counter)


def filter_by_day(tbl, date_str, weekday):
    return [r for r in tbl if r[weekday] and r['start_date'] <= date_str <= r['end_date']]


def filter_by_day_passengers(tbl, day):
    return [r for r in tbl if r['day'].lower() == day]


def station_super_set(tbls):
    return set(row['station_name'] for table in tbls for row in table)


def passengers_and_buses_per_hour_non_pivoted(output_folder, buses, trains, passengers, all_stations):
    """Creates a csv with station, day of week, hour of day, average passengers and number of buses"""
    output_file = os.path.join(output_folder, 'buses_and_passengers_per_station_per_day_per_hour.csv')

    def build_count(tbl):
        c = Counter()
        for r in tbl:
            stop_code = r['station_name']
            hour = r['hour']
            for day in (day for day in WEEKDAYS if r[day]):
                c[(stop_code, hour, day)] += 1
        return c

    # aggregate by train, day & hour
    buses_counter = build_count(buses)
    trains_counter = build_count(trains)
    passengers_counter = {(r['station_name'], int(r['hour']), r['day'].lower()): r['avg'] for r in passengers}

    with open(output_file, 'w', encoding='utf8') as out_f:
        writer = csv.DictWriter(out_f,
                                fieldnames=['station_name', 'hour', 'day', 'passengers', 'buses', 'trains'],
                                lineterminator='\n')
        writer.writeheader()
        for station in all_stations:
            for day in WEEKDAYS:
                for hour in range(24):
                    k = (station, hour, day)
                    writer.writerow({'station_name': station,
                                     'hour': hour,
                                     'day': day,
                                     'passengers': '%.2f' % float(passengers_counter.get(k, 0)),
                                     'buses': buses_counter[k],
                                     'trains': trains_counter[k]})


def main(all_buses_filename, all_trains_filename, all_passengers_filename, output_folder, start_date):
    def avg(l):
        s = sum(1 for x in l if x is not None)
        return sum(x for x in l if x is not None) / s if s != 0 else None

    print("Loading data")
    trains = load_train_or_bus_data(all_buses_filename)
    buses = load_train_or_bus_data(all_trains_filename)
    passengers = load_passengers_data(all_passengers_filename)

    all_stations = station_super_set([trains, buses, passengers])
    print("There are %d stations" % len(all_stations))

    date_range = [datetime.datetime.strptime(start_date, '%Y-%m-%d').date() + datetime.timedelta(days=d)
                  for d in range(7)]
    print("Working on days between %s and %s" % (date_range[0], date_range[-1]))

    passengers_and_buses_per_hour_non_pivoted(output_folder, buses, trains, passengers, all_stations)

    for date in date_range:
        date_str = date.strftime('%Y-%m-%d')
        day = date.strftime('%A').lower()
        daily_trains = filter_by_day(trains, date_str, day)
        print_all_trips(os.path.join(output_folder, 'all_trains_%s.csv' % day), daily_trains)
        daily_bus = filter_by_day(buses, date_str, day)
        print_all_trips(os.path.join(output_folder, 'all_buses_%s.csv' % day), daily_trains, buses=True)
        print(date_str, day, '%d train journeys' % len(daily_trains), '%d bus journeys' % len(daily_bus))
        # create sub data frame with only buses/trains in specific day
        trains_day = create_pivot(daily_trains, all_stations)
        buses_day = create_pivot(daily_bus, all_stations)
        passengers_day = create_pivot_passengers(filter_by_day_passengers(passengers, day), all_stations)

        add_agg_row(trains_day, sum, 'Sum')
        add_agg_row(buses_day, sum, 'Sum')
        add_agg_row(passengers_day, sum, 'Sum')

        output_pivot(os.path.join(output_folder, 'buses_%s.csv' % day), buses_day, ['Sum'])
        output_pivot(os.path.join(output_folder, 'trains_%s.csv' % day), trains_day, ['Sum'])
        output_pivot(os.path.join(output_folder, 'passengers_%s.csv' % day), passengers_day, ['Sum'])

        # ratio buses-trains
        bus_to_train = calculate_ratio(buses_day, trains_day)
        add_agg_row(bus_to_train, avg, 'Avg')
        output_pivot(os.path.join(output_folder, 'bus_train_%s.csv' % day), bus_to_train, ['Avg'])

        # ratio passengers-trains
        passenger_to_train = calculate_ratio(passengers_day, buses_day)
        add_agg_row(passenger_to_train, avg, 'Avg')
        output_pivot(os.path.join(output_folder, 'passenger_bus_%s.csv' % day), passenger_to_train, ['Avg'])

    print("All Done!")


def to_google_sheets(output_folder, client_secret_path):
    names = ('Trains', 'Buses', 'Passengers', 'Bus/Train', 'Passengers/Buses')
    base_file_names = ('trains_%s.csv', 'buses_%s.csv', 'passengers_%s.csv', 'bus_train_%s.csv', 'passenger_bus_%s.csv')
    for name, base_file_name in zip(names, base_file_names):
        spreadsheet_id = csvs_to_gsheet(name,
                                        [os.path.join(output_folder, base_file_name % day) for day in WEEKDAYS],
                                        WEEKDAYS, client_secret_path=client_secret_path)
        auto_fit_column_width(spreadsheet_id, client_secret_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--all_buses', required=True)
    parser.add_argument('--all_trains', required=True)
    parser.add_argument('--all_passengers', required=True)
    parser.add_argument('--output_folder', required=True)
    parser.add_argument('--start_date', help="First day of the week to look at; yyyy-mm-dd format")
    parser.add_argument('--gsheet_secret')
    parser.set_defaults(dont_fix_times=False)

    args = parser.parse_args()
    main(all_buses_filename=args.all_buses,
         all_trains_filename=args.all_trains,
         all_passengers_filename=args.all_passengers,
         output_folder=args.output_folder, start_date=args.start_date)
    if args.gsheet_secret:
        to_google_sheets(args.output_folder, args.gsheet_secret)

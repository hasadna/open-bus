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
from gtfs.bus2train.gsheet_tools import csvs_to_gsheet
import datetime

WEEKDAYS = ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday')


def output_pivot(filename, tbl):
    print("Writing", filename)
    with open(filename, 'w', encoding='utf8') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(["station"] + [str(h) for h in range(24)])
        for station in sorted(tbl):
            writer.writerow([station] + [tbl[station][h] for h in range(24)])


def calculate_ratio(tbl_a, tbl_b):
    """This function assumes to two tables have the same keys """
    return {k1: {k2: '%.02f' % (tbl_a[k1][k2] / tbl_b[k1][k2]) if tbl_b[k1][k2] != 0 else ''
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


def main(all_buses, all_trains, all_passengers, output_folder, start_date):
    print("Loading data")
    trains, buses, passengers = load_data(tbl=all_trains), load_data(tbl=all_buses), load_data(tbl=all_passengers)

    print("Cleaning data")
    trains = apply_to_field(rename_fields(trains), 'hour', lambda s: int(float(s)))
    buses = apply_to_field(rename_fields(buses), 'hour', lambda s: int(float(s)))
    passengers = apply_to_field(rename_fields(passengers), 'hour', int)
    passengers = apply_to_field(passengers, 'avg', lambda s: float(s) if s != '' else 0)

    fix_times(buses)
    fix_times(trains)

    all_stations = station_super_set([trains, buses, passengers])
    print("There are %d stations" % len(all_stations))

    date_range = [datetime.datetime.strptime(start_date, '%Y-%m-%d').date() + datetime.timedelta(days=d)
                  for d in range(7)]
    print("Working on days between %s and %s" % (date_range[0], date_range[-1]))

    passengers_and_buses_per_hour_non_pivoted(output_folder, buses, trains, passengers, all_stations)

    for date in date_range:
        date_str = date.strftime('%Y-%m-%d')
        day = date.strftime('%A').lower()
        print(date_str, day)
        # create sub data frame with only buses/trains in specific day
        trains_day = create_pivot(filter_by_day(trains, date_str, day), all_stations)
        buses_day = create_pivot(filter_by_day(buses, date_str, day), all_stations)
        passengers_day = create_pivot_passengers(filter_by_day_passengers(passengers, day), all_stations)
        output_pivot(os.path.join(output_folder, 'buses_%s.csv' % day), buses_day)
        output_pivot(os.path.join(output_folder, 'trains_%s.csv' % day), trains_day)
        output_pivot(os.path.join(output_folder, 'passengers_%s.csv' % day), passengers_day)

        # ratio buses-trains
        output_pivot(os.path.join(output_folder, 'bus_train_%s.csv' % day), calculate_ratio(buses_day, trains_day))

        # ratio passengers-trains
        output_pivot(os.path.join(output_folder, 'passenger_bus_%s.csv' % day),
                     calculate_ratio(passengers_day, buses_day))

    print("All Done!")


def to_google_sheets(output_folder, client_secret_path):
    csvs_to_gsheet('Trains', [os.path.join(output_folder, 'trains_%s.csv' % day) for day in WEEKDAYS],
                   WEEKDAYS, client_secret_path=client_secret_path)
    csvs_to_gsheet('Buses', [os.path.join(output_folder, 'buses_%s.csv' % day) for day in WEEKDAYS],
                   WEEKDAYS, client_secret_path=client_secret_path)
    csvs_to_gsheet('Passengers', [os.path.join(output_folder, 'passengers_%s.csv' % day) for day in WEEKDAYS],
                   WEEKDAYS, client_secret_path=client_secret_path)
    csvs_to_gsheet('Bus/Train', [os.path.join(output_folder, 'bus_train_%s.csv' % day) for day in WEEKDAYS],
                   WEEKDAYS, client_secret_path=client_secret_path)
    csvs_to_gsheet('Passenger/Bus', [os.path.join(output_folder, 'passenger_bus_%s.csv' % day) for day in WEEKDAYS],
                   WEEKDAYS, client_secret_path=client_secret_path)


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
    main(all_buses=args.all_buses, all_trains=args.all_trains, all_passengers=args.all_passengers,
         output_folder=args.output_folder,  start_date=args.start_date)
    if args.gsheet_secret:
        to_google_sheets(args.output_folder, args.gsheet_secret)

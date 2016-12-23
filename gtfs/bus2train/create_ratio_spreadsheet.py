"""
This Script is for making a spreadsheet for each day of ratio between buses and trains.
Three parameters are needed:
1. path to csv of all_buses (output of - postgres/bus2train/all_buses_near_train_stations.sql)
2. path to csv of all_trains (output of - postgres/bus2train/all_train_hours.sql)
3. path to csv of passengers average data (output of - http://data.obudget.org/queries/839)
3. output folder

please note the script is sensitive to the csv structure. So any change in query will result with fail of this script.

script also fixes bus and trains times as 25:00 and changes days accordingly"
"""

import pandas as pd
import numpy as np
import argparse
import csv

TRAIN_STATIONS = (17000, 17002, 17004, 17006, 17008, 17010, 17012, 17014, 17016, 17018, 17020, 17022, 17024, 17026, 17028, 17030, 17032, 17034, 17036, 17038, 17040, 17042, 17044, 17046, 17048, 17050, 17052, 17054, 17056, 17058, 17060, 17062, 17064, 17066, 17068, 17070, 17072, 17074, 17076, 17078, 17080, 17082, 17084, 17086, 17088, 17090, 17092, 17094, 17096, 17098, 17100, 17102, 17104, 17106, 17108, 17109, 17110, 17111, 17112, 17113, 17114, 'All')


def output_ratio(ratio, typ, output_folder, day):  # type: bus_train or passenger_train
    ratio['average'] = ratio.mean(axis=1)
    path = output_folder + "\\ratio_" + typ + "_" + day + ".csv"
    ratio.to_csv(path, float_format='%.2f')
    print("Created and saved: ratio " + typ + "_" + day)


def output_pivot(tbl_bus, tbl_train, tbl_passengers, output_folder, day):
    tbl_train.to_csv(output_folder + "\\trains_" + day + ".csv", float_format='%.0f')
    print("Created and saved: trains " + day)
    tbl_bus.to_csv(output_folder + "\\buses_" + day + ".csv", float_format='%.0f')
    print("Created and saved: buses " + day)
    tbl_passengers.to_csv(output_folder + "\\passengers_" + day + ".csv", float_format='%.2f')
    print("Created and saved: passengers " + day)


def calculate_ratio(tbl_a, tbl_b):
    ratio_table = pd.DataFrame().reindex_like(tbl_b)
    for i in range(0, 24):
        if i in tbl_a.columns and i in tbl_b.columns:
            ratio_table[i] = tbl_a[i] / tbl_b[i]
    ratio_table = ratio_table.replace(np.inf, np.nan, regex=True)
    ratio_table = ratio_table.drop('All', 1)
    ratio_table = ratio_table.drop('All', 0)
    return ratio_table


def create_pivot(buses, trains, passengers):
    tbl_bus = buses.pivot_table(values='bus_time', index='train_stop', columns='hour',
                                 aggfunc=len, fill_value=0, margins=True)
    tbl_bus = tbl_bus.reindex(index=TRAIN_STATIONS, fill_value=0)  # to fill stations with missing data
    tbl_train = trains.pivot_table(values='train_time', index='stop_code', columns='hour',
                                    aggfunc=len, fill_value=0, margins=True)
    tbl_train = tbl_train.reindex(index=TRAIN_STATIONS, fill_value=0)  # to fill stations with missing data
    tbl_passengers = passengers.pivot_table(values='avg', index='station_code', columns='hour',
                                            fill_value=0, margins=True)
    tbl_passengers = tbl_passengers.reindex(index=TRAIN_STATIONS, fill_value=0)  # to fill stations with missing data
    return tbl_bus, tbl_train, tbl_passengers


def load_data(tbl):
    data = pd.read_csv(tbl, low_memory=False)
    return data


# this part is associated with the SQL queries so if any change made in query please change here too.

def fix_time_train(all_trains):
    text = ''
    count_changes = 0
    with open(all_trains, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        line = next(reader, None)  # skip the headers
        line = ','.join(map(str, line)) + '\n'
        text += line
        for line in reader:
            lst = line
            if float(line[3]) >= 24:
                # fix hour
                lst[3] = (float(line[3])-24)
                # fix days
                days = line[4:11]
                for i in range(7):
                    lst[i+4] = days[i-1]
                count_changes += 1
            lst = ','.join(map(str, lst)) + '\n'
            text += lst
    with open(all_trains, 'w', encoding='utf8') as f:
        f.write(text)
    return count_changes


def fix_time_buses(all_buses):
    text = ''
    count_changes = 0
    with open(all_buses, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        line = next(reader, None)  # skip the headers
        line = ','.join(map(str, line)) + '\n'
        text += line
        for line in reader:
            lst = line
            if float(line[3]) >= 24:
                # fix hour
                lst[3] = (float(line[3])-24)
                # fix days
                days = line[6:13]
                for i in range(7):
                    lst[i+6] = days[i-1]
                count_changes += 1
            lst = ','.join(map(str, lst)) + '\n'
            text += lst
    with open(all_buses, 'w', encoding='utf8') as f:
        f.write(text)
    return count_changes


def main(all_buses, all_trains, all_passengers, output_folder, dont_fix_times):
    if not dont_fix_times:
        changes = fix_time_buses(all_buses)
        print("Finished fixing buses times, %d rows were changed" % changes)
        changes = fix_time_train(all_trains)
        print("Finished fixing trains times, %d rows were changed" % changes)

    trains, buses, passengers = load_data(tbl= all_trains), load_data(tbl= all_buses), load_data(tbl= all_passengers)
    print("Data uploaded")

    for day in ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'):
        train_column = 'train_' + day
        bus_column = 'bus_' + day
        # create sub data frame with only buses/trains in specific day
        trains_day = trains[(trains[str(train_column)] == True)].drop_duplicates()
        buses_day = buses[(buses[str(bus_column)] == True)].drop_duplicates()
        passengers_day = passengers[(passengers['day'].str.strip() == day.title())]
        tbl_bus, tbl_train, tbl_passengers = create_pivot(buses_day, trains_day, passengers_day)
        output_pivot(tbl_bus, tbl_train, tbl_passengers, output_folder, day)
        # ratio buses-trains
        ratio = calculate_ratio(tbl_bus, tbl_train)
        output_ratio(ratio, 'bus_train', output_folder, day)

        # ratio passengers-trains
        ratio = calculate_ratio(tbl_passengers, tbl_bus)
        output_ratio(ratio, 'passenger_bus', output_folder, day)
    print("All Done!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--all_buses', required=True)
    parser.add_argument('--all_trains', required=True)
    parser.add_argument('--all_passengers', required=True)
    parser.add_argument('--output_folder', required=True)
    parser.add_argument('--dont_fix_times')
    parser.set_defaults(dont_fix_times=False)

    args = parser.parse_args()
    main(all_buses=args.all_buses, all_trains=args.all_trains, all_passengers=args.all_passengers,
        output_folder=args.output_folder, dont_fix_times=args.dont_fix_times)

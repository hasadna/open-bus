# -*- coding: utf-8 -*-
"""
About Script
This Script is for making a spreadsheet for each day of ratio between buses and trains.
Three parameters are needed:
1. path to csv of all_buses (output of - postgres/bus2train/all_buses_near_train_stations.sql)
2. path to csv of all_trains (output of - postgres/bus2train/all_train_hours.sql)
3. path to csv of passengers average data (output of - http://data.obudget.org/queries/839)
4. path to csv of waiting time data (output of - postgres/bus2train/waiting_time_for_bus.sql)
5. output folder
6. CLIENT SECRET - Google Sheets API KEY. here instructions to get key: nhttps://github.com/daphshez/gsheet_tools

please note the script is sensitive to the csv structure. So any change in query will result with fail of this script.

script also fixes bus and trains times as 25:00 and changes days accordingly

About Pandas
pandas is a python library for data manipulation and analysis of data.
How to query Pandas data frames: http://pandas.pydata.org/pandas-docs/stable/comparison_with_sql.html
Pivots in Pandas: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.pivot_table.html
"""

import pandas as pd
import numpy as np
import argparse
import os
import gsheet_tools

TRAIN_STATIONS_CODE = (17000, 17002, 17004, 17006, 17008, 17010, 17012, 17014, 17016, 17018, 17020, 17022, 17024, 17026, 17028, 17030, 17032, 17034, 17036, 17038, 17040, 17042, 17044, 17046, 17048, 17050, 17052, 17054, 17056, 17058, 17060, 17062, 17064, 17066, 17068, 17070, 17072, 17074, 17076, 17078, 17080, 17082, 17084, 17086, 17088, 17090, 17092, 17094, 17096, 17098, 17100, 17102, 17104, 17106, 17108, 17109, 17110, 17111, 17112, 17113, 17114, 'All')
TRAIN_STATIONS = ("אופקים", "אשדוד עד הלום", "אשקלון", "באר יעקב", "באר שבע מרכז", "באר שבע-צפון", "בית יהושע", "בית שאן", "בית שמש", "בני ברק", "בנימינה", "בת גלים", "בת ים יוספטל", "בת ים קוממיות", "דימונה", "הוד השרון", "הרצליה", "השלום", "חדרה מערב", "חולון וולפסון", "חוף הכרמל", "חוצות מפרץ", "חיפה מרכז", "יבנה מזרח", "יבנה מערב", "ירושלים גן חיות", "ירושלים מלחה", "כפר ברוך", "כפר חבד", "כפר יהושע", "כפר סבא", "לב המפרץ", "להבים רהט", "לוד", "לוד-גני אביב", "מודיעין מרכז", "נהריה", "נת-בג", "נתיבות", "נתניה", "נתניה קריית ספיר", "סגולה", "עכו", "עפולה", "עתלית", "פאתי מודיעין", "צומת חולון", "קיסריה פרדס חנה", "קרית אריה", "קרית גת", "קרית חיים", "קרית מוצקין", "ראש העין-צפון", "ראשונים", "רחובות", "רמלה", "רשל''צ משה דיין", "שדרות", "תא אוניברסיטה", "תל אביב ההגנה", "תל אביב מרכז", 'All')

WEEKDAYS = ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday')


def to_google_sheets(output_folder, client_secret_path):
    names = ('Trains', 'Buses', 'Passengers', 'Bus/Train', 'Passengers/Buses', 'waiting_time', 'no_bus')
    base_file_names = (
        'train_%s.csv', 'bus_%s.csv', 'passengers_%s.csv', 'ratio_bus_train_%s.csv', 'ratio_passengers_bus_%s.csv',
        'wait_time_%s.csv', 'no_bus_%s.csv')
    for name, base_file_name in zip(names, base_file_names):
        spreadsheet_id = gsheet_tools.csvs_to_gsheet(name,
                                                     [os.path.join(output_folder, base_file_name % day) for day in
                                                      WEEKDAYS],
                                                     [s[:3] for s in WEEKDAYS], client_secret_path=client_secret_path)
        # Format Sheets
        gsheet_tools.auto_fit_column_width(spreadsheet_id, client_secret_path)
        if name in ('Trains', 'Buses', 'Passengers'):
            gsheet_tools.conditional_formatting(spreadsheet_id=spreadsheet_id, type='ROW',
                                                client_secret_path=client_secret_path, rows = len(TRAIN_STATIONS))
        elif name in ('Passengers/Buses', 'waiting_time', 'no_bus'):
            gsheet_tools.conditional_formatting(spreadsheet_id=spreadsheet_id, type='SHEET',
                                                client_secret_path=client_secret_path, rows = len(TRAIN_STATIONS),
                                                larger_green =False)
        else:
            gsheet_tools.conditional_formatting(spreadsheet_id=spreadsheet_id, type='SHEET',
                                                client_secret_path=client_secret_path, rows = len(TRAIN_STATIONS))


def output_table_to_csv(table, type, output_folder, day, precsion):
    file_name = type + "_" + day + ".csv"
    float_format = '%.'+ str(precsion) + 'f'
    table.to_csv(output_folder + "\\" + file_name, float_format = float_format, encoding = 'utf-8')
    print("Created and saved: " + file_name)


def calculate_ratio(tbl_a, tbl_b):
    ratio_table = pd.DataFrame().reindex_like(tbl_b)
    for i in range(0, 24):
        if i in tbl_a.columns and i in tbl_b.columns:
            ratio_table[i] = tbl_a[i] / tbl_b[i]
    ratio_table = ratio_table.replace(np.inf, np.NaN, regex=True)
    ratio_table = ratio_table.drop('All', 1)
    ratio_table = ratio_table.drop('All', 0)
    ratio_table['average'] = ratio_table.mean(axis=1)
    return ratio_table


def create_pivot(table, values, index, columns, aggfunc, summary_func, fill_value):
    pivot_table = table.pivot_table(values=values, index=index, columns=columns,
                                 aggfunc=aggfunc, fill_value=fill_value, margins=False)
    pivot_table = pivot_table.reindex(index=TRAIN_STATIONS, fill_value=0)  # to fill stations with missing data
    # create summary column
    if summary_func == 'sum':
        pivot_table['All'] = pivot_table.sum(axis=1)
        pivot_table.loc['All'] = pivot_table.sum()
    elif summary_func == 'avg':
        pivot_table['Avg'] = pivot_table.mean(axis=1)
        pivot_table.loc['Avg'] = pivot_table.mean()
    return pivot_table


def load_data(tbl):
    data = pd.read_csv(tbl, low_memory=False)
    return data


# this part is associated with the SQL queries so if any change made in query please change here too.

def fix_times(table):
    def func(x):
        if x >= 24:
            return x - 24
        else:
            return x
    over_24 = table[(table['hour'] >= 24)]
    less_24 = table[(table['hour'] < 24)]
    over_24['hour'] = over_24['hour'].apply(func)
    over_24.rename(inplace=True, columns={"sunday": "monday",
                                          "monday":"tuesday",
                                          "tuesday":"wednesday",
                                          "wednesday":"thursday",
                                          "thursday":"friday",
                                          "friday":"saturday",
                                          "saturday":"sunday"})
    return pd.concat([over_24, less_24])


def main(all_buses, all_trains, all_passengers, min_time, output_folder, client_secret):

    print("Uploading Data...")
    trains, buses, passengers = load_data(tbl=all_trains), load_data(tbl=all_buses), load_data(tbl=all_passengers)
    wait_time = load_data(tbl= min_time)
    print("Data uploaded!")

    print("\nFixing times...")
    buses = fix_times(buses)
    trains = fix_times(trains)
    wait_time = fix_times(wait_time)
    print("Finished fixing")

    print("\nCreating Pivots...")
    for day in WEEKDAYS:
        print("---------"+day+"---------")
        # create sub data frame with only buses/trains in specific day
        trains_day = trains[(trains[str(day)] == True)].drop_duplicates()  # drop duplicates because if trip was before on Monday and Friday and on Sunday and Friday it was 2 rows. when we take only friday we won't to drop duplicates
        buses_day = buses[(buses[str(day)] == True)].drop_duplicates()
        passengers_day = passengers[(passengers['day'].str.strip() == day.title())]
        wait_time_day = wait_time[wait_time[day] == True]
        no_bus = wait_time_day[pd.isnull(wait_time_day).any(axis=1)]  # get all rows where there is a train but no bus after

        # create pivots
        tbl_bus = create_pivot(table=buses_day, columns='hour', aggfunc=len, index='train_stop_name', values='bus_time',
                               fill_value=0, summary_func='sum')
        tbl_train = create_pivot(table=trains_day, columns='hour', aggfunc=len, index='stop_name', values='train_time',
                                 fill_value=0, summary_func='sum')
        tbl_passengers = create_pivot(table=passengers_day, columns='hour', aggfunc=np.mean, index='stop_name',
                                      values='avg', fill_value=0, summary_func='sum')
        tbl_wait_time = create_pivot(table=wait_time_day, columns='hour', aggfunc=np.mean, index='stop_name',
                                      values='waiting_time', fill_value=None, summary_func='avg')
        tbl_no_bus = create_pivot(table=no_bus, columns='hour', aggfunc=len, index='stop_name',
                                      values='waiting_time', fill_value=0, summary_func='avg')

        # output pivots
        output_table_to_csv(tbl_bus, type='bus', precsion=0, output_folder=output_folder, day=day)
        output_table_to_csv(tbl_train, type='train', precsion=0, output_folder=output_folder, day=day)
        output_table_to_csv(tbl_passengers, type='passengers', precsion=2, output_folder=output_folder, day=day)
        output_table_to_csv(tbl_wait_time, type='wait_time', precsion=2, output_folder=output_folder, day=day)

        # ratio buses-trains
        ratio_tbl = calculate_ratio(tbl_bus, tbl_train)
        output_table_to_csv(ratio_tbl, type='ratio_bus_train', precsion=2, output_folder=output_folder, day=day)

        # ratio passengers-trains
        ratio_tbl = calculate_ratio(tbl_passengers, tbl_bus)
        output_table_to_csv(ratio_tbl, type='ratio_passengers_bus', precsion=2, output_folder=output_folder, day=day)

        # ratio train with no bus to all trains
        ratio_tbl = calculate_ratio(tbl_no_bus, tbl_train)
        ratio_tbl *= 100  # make percentage
        ratio_tbl = ratio_tbl.drop('average', 1)
        ratio_tbl = ratio_tbl.replace(np.NaN, 0, regex=True)
        output_table_to_csv(ratio_tbl, type='no_bus', precsion=2, output_folder=output_folder, day=day)

    print("All pivots and ratios created!")
    if client_secret != '':
        print("\nExporting to Google Sheets...")
        # output to Google Sheets
        to_google_sheets(output_folder, client_secret_path=client_secret)
        print("Finished exporting to Google Sheets!")

    print("\nAll Done!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--all_buses', required=True)
    parser.add_argument('--all_trains', required=True)
    parser.add_argument('--all_passengers', required=True)
    parser.add_argument('--min_time', required=True)
    parser.add_argument('--output_folder', required=True)
    parser.add_argument('--client_secret', default='')


    args = parser.parse_args()
    main(all_buses=args.all_buses, all_trains=args.all_trains, all_passengers=args.all_passengers,
        output_folder=args.output_folder, min_time=args.min_time, client_secret=args.client_secret)

# -*- coding: utf-8 -*-

# Written by:
#   yehuda nurieli - kv100100@gmail.com
#   Rafi Gana      - rafig93@gmail.com
# Written for "the public knowledge workshop"
# Non-commercial use only

import csv
from datetime import datetime, timedelta
from os import path

import db_insert

root = ""

STOPS_FILENAME = "files/stops.txt"
# columns indexes
STOP_CODE_COL = 1

ROUTES_FILENAME = "files/routes.txt"
TRIPS_FILENAME = "files/trips.txt"

STOP_TIMES_FILENAME = "files/stop_times.txt"
# columns indexes
ARRIVAL_TIME_COL = 1
STOP_ID_COL = 3

#files to parse
FILE_NAMES_LIST=[STOPS_FILENAME, ROUTES_FILENAME, TRIPS_FILENAME, STOP_TIMES_FILENAME]

def _get_name_of_file_without_ext(f):
    return f[:f.rfind("."):].split('/')[-1]

def csv_file_to_list(file_name):
    with open(path.join(root, file_name)) as f:
        first=True

        # [columns list, lines list]
        list_to_return = []
        file_lines = csv.reader(f)

        # list to line data
        list_of_line=[]

        for line in file_lines:
            if first:
                list_to_return.append(line)
                first=False

            else:
                list_of_line.append(line)

        list_to_return.append(list_of_line)
        return list_to_return
        
for f in FILE_NAMES_LIST:
    f_name = _get_name_of_file_without_ext(f)
    file_data = csv_file_to_list(f)

    col, rows = file_data

    print("start working on: {}. columns list: {}".format(f_name, col))

    db_insert.make_schema(f_name, col)
    db_insert.insert_to_db(f_name, col, rows)
    db_insert.make_index(f_name, col)
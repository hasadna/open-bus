# -*- coding: utf-8 -*-

# Written for "the public knowledge workshop"
# Non-commercial use only

import csv
from datetime import datetime, timedelta
from os import path

import sqlite3
import sys

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

DB_FILE_NAME = "static.db"

CSV_FILE_NAMES = [STOPS_FILENAME, ROUTES_FILENAME, TRIPS_FILENAME, STOP_TIMES_FILENAME]


def _get_name_of_file_without_ext(f):
    return f[:f.rfind("."):].split('/')[-1]


def csv_file_to_list(file_name):
    with open(path.join(root, file_name)) as f:
        first = True

        # [columns list, lines list]
        list_to_return = []
        file_lines = csv.reader(f)

        # list to line data
        list_of_line = []

        for line in file_lines:
            if first:
                list_to_return.append(line)
                first = False

            else:
                list_of_line.append(line)

        list_to_return.append(list_of_line)
        return list_to_return


def exec_sql_query(query, db_file_name=DB_FILE_NAME):
    conn = sqlite3.connect(db_file_name)
    c = conn.cursor()

    c.execute(query)

    conn.commit()
    conn.close()


def insert_to_db(table_name, columns, entries, db_file_name=DB_FILE_NAME):
    conn = sqlite3.connect(db_file_name)
    c = conn.cursor()

    columns = """ (""" + ','.join([column for column in columns]) + """) values """
    print(columns)
    query = "insert into {table_name} {columns}".format(table_name=table_name, columns=columns)

    values = ""
    for entry in entries:
        datarow = ""
        for col in entry:
            datarow += ',"{}"'.format(col)
        exec_query = "{query} ({values});".format(query=query, values=datarow[1:])
        # print(exec_query)
        # sys.exit()
        c.execute(exec_query)

    conn.commit()
    conn.close()

    print("table {} db close".format(table_name))


def make_index(table_name, column_names=None, db_file_name=DB_FILE_NAME):
    query = str("""CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}"""
                .format(index_name=table_name + '_ind', table_name=table_name))

    if column_names is not None:
        column_names = ",".join(column_names)
        query += "({})".format(column_names)

    query += ' ;'
    print(query)
    exec_sql_query(query, db_file_name)


def make_schema(table_name, columns, db_file_name=DB_FILE_NAME):
    query = str("""create table  IF NOT EXISTS  {} (""" + ','.join(
        [column + ' VARCHAR(120) ' for column in columns]) + """);""").format(table_name)
    print(query)
    exec_sql_query(query, db_file_name)


def select(query, db_file_name=DB_FILE_NAME):
    conn = sqlite3.connect(db_file_name)
    return conn.execute(query)


def insert_csv_files(csv_file_names=CSV_FILE_NAMES, db_file_name=DB_FILE_NAME):
    for f in csv_file_names:
        f_name = _get_name_of_file_without_ext(f)
        file_data = csv_file_to_list(f)

        col, rows = file_data

        print("start working on: {}. columns list: {}".format(f_name, col))

        make_schema(f_name, col, db_file_name)
        insert_to_db(f_name, col, rows, db_file_name)
        make_index(f_name, col, db_file_name)

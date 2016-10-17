"""
צורת ההמרה של הקבצים לדאטא בייס:
עבור כל קובץ GTFS נוצר טבלה ששמה הוא שם הקובץ, ועבור כל עמודה בקובץ נוצרת עמודה בטבלה עם אותו שם.
!- שימו לב -! כל המשתנים נכנסים לטבלה כסטרינג/string,
 במידה ומישהו מעוניין להוסיף משהו שיבדוק את סוג העמדה וע"פ זה יצור סוג זהה בDB הוא יותר ממוזמן.

 How to run:
 call this script and give a single parameter, a name of directory that contains the gtfs file (extracted from the zip).

"""

import sqlite3
import sys
from os import path

STOPS_FILENAME = "stops.txt"
ROUTES_FILENAME = "routes.txt"
TRIPS_FILENAME = "trips.txt"
STOP_TIMES_FILENAME = "stop_times.txt"
FILE_NAMES_LIST = [STOPS_FILENAME, ROUTES_FILENAME, TRIPS_FILENAME, STOP_TIMES_FILENAME]


def exec_sql_query(query):
    conn = sqlite3.connect("static.db")
    c = conn.cursor()

    c.execute(query)

    conn.commit()
    conn.close()


def insert_to_db(table_name, columns, entries):
    conn = sqlite3.connect("static.db")
    c = conn.cursor()

    columns = """ (""" + ','.join([column for column in columns]) + """) values """
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


def make_index(table_name, column_names=None):
    query = str("""CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}"""
                .format(index_name=table_name + '_ind', table_name=table_name))

    if column_names is not None:
        column_names = ",".join(column_names)
        query += "({})".format(column_names)

    query += ' ;'
    print(query)
    exec_sql_query(query)


def make_schema(table_name, columns):
    query = str("""create table  IF NOT EXISTS  {} (""" + ','.join(
        [column + ' VARCHAR(120) ' for column in columns]) + """);""").format(table_name)
    print(query)
    exec_sql_query(query)


def main(gtfs_folder):
    def _get_name_of_file_without_ext(f):
        return f[:f.rfind("."):]

    for full_file_name in FILE_NAMES_LIST:
        table_name = _get_name_of_file_without_ext(full_file_name)
        with open(path.join(gtfs_folder, full_file_name)) as f:
            col = next(f)
            rows = (line for line in f)

            print("start working on: {}. columns list: {}".format(table_name, col))

            make_schema(table_name, col)
            insert_to_db(table_name, col, rows)
            make_index(table_name, col)


if __name__ == '__main__':
    main(sys.argv[1])

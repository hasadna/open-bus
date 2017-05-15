import os
from jinja2 import Environment, FileSystemLoader
import csv
import sys
import psycopg2
from configparser import ConfigParser
import datetime


def parent_dir(p):
    return os.path.abspath(os.path.join(p, os.pardir))


GTFS_SCRIPT_DIR = parent_dir(parent_dir(__file__))
DATA_DIR = os.path.join(GTFS_SCRIPT_DIR, 'data')
TEMPLATES_PATH = os.path.join(GTFS_SCRIPT_DIR, 'templates')

# data files
MAPPING_FILE = "mapping.txt"

# template files
CONNECTION_TEMPLATE_FILE_NAME = "ps_connection_string.template"
QUERY_TEMPLATE_FILE_NAME = "ps_query.template"


def parse_config(config_file_name):
    with open(config_file_name) as f:
        # add section header because config parser requires it
        config_file_content = '[Section]\n' + f.read()
    config = ConfigParser()
    config.read_string(config_file_content)
    return {k: v for (k, v) in config['Section'].items()}


def build_connection_string(db_config, conn_template):
    """
    build connection string from data and template
    """
    return conn_template.render(data=db_config)


def connect(conn_string):
    """
    given a connection string creates connection to ps db
    """
    try:
        return psycopg2.connect(conn_string)
    except psycopg2.Error as e:
        print("Unable to connect to database. {}".format(e))


def load_mapping(mapping_file):
    """Returns a map from table name, to a list object of tuples of column name and data type"""
    mapping = {}
    current_table = None
    with open(mapping_file, 'r') as f:
        lines = (line.strip() for line in f)
        for line in lines:
            if line.startswith('TABLE '):
                current_table = line.split(' ')[1]
                mapping[current_table] = []
            else:
                line_arr = line.strip().split(" ")
                if len(line_arr) >= 2:
                    col_name, col_type = line_arr[0], line_arr[1]
                    mapping[current_table].append((col_name, col_type))
    return mapping


def get_table_name(file_path):
    return "gtfs_" + os.path.splitext(os.path.basename(file_path))[0]


def progenum(iterable, freq):
    """A primitive progress bar"""
    i = 0
    for i, r in enumerate(iterable):
        yield r
        if i % freq == 0:
            print(' %s Read %d records' % (datetime.datetime.now(), i))
    print(' Total number of records: %d' % i)


def insert_file_to_db(file_path, cursor, table_name, columns, query_template, conn_obj):
    """
    file path - the path of the file containing data, notice - the name
    of the file must match to the table e.g. agency.txt to table agency
    conn_obj - connection object to postgres received in connect method
    table_name - name of the table to write to
    mapping -  list of tuples of column name and data type
    query template - template for queries in postgres
    """
    print("Importing data to table %s" % table_name)
    with open(file_path, encoding='utf-8') as f:
        # find indices of columns in the postgres actual table
        reader = progenum(csv.DictReader(f), 1000)
        for row in reader:
            values = []
            placeholder = []
            for col_name, col_type in columns:
                if col_type == "integer" and row[col_name] == '':
                    values.append(None)
                else:
                    values.append(row[col_name])
                placeholder.append("%s")

            query = query_template.render(columns=list(zip(*columns))[0], values=placeholder, table_name=table_name)
            try:
                cursor.execute(query, values)
                conn_obj.commit()
            except Exception as e:
                print(e)
                print(row)
                conn_obj.rollback()


def insert_folder_to_db(folder, db_config):
    env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
    conn_template = env.get_template(CONNECTION_TEMPLATE_FILE_NAME)
    connection_string = build_connection_string(db_config, conn_template)
    conn_obj = connect(connection_string)
    cursor = conn_obj.cursor()
    query_template = env.get_template(QUERY_TEMPLATE_FILE_NAME)
    mapping = load_mapping(os.path.join(DATA_DIR, MAPPING_FILE))

    for file in os.listdir(folder):
        table_name = get_table_name(file)
        if table_name in mapping:
            try:
                insert_file_to_db(os.path.join(folder, file), cursor,
                                  table_name, mapping[table_name], query_template, conn_obj)
            except Exception as e:
                print(file + " failed")
                print(e)
        else:
            print("Mapping doesn't contain table matching %s, can't import" % table_name)

    conn_obj.close()


def main():
    config = parse_config(sys.argv[1])
    insert_folder_to_db(config["gtfs_folder"], config)


if __name__ == '__main__':
    main()

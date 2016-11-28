import psycopg2
import os
from psycopg2.extensions import AsIs
from siri import siri_parser


RESPONSE_INSERT_QUERY = "INSERT INTO siri_raw_responses(response_xml) VALUES(%s) RETURNING id;"

DB_SCHEMA_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def connect(**kwargs):
    conn_string = "dbname={name} user={user} host={host} password={password}".format(**kwargs)
    return psycopg2.connect(conn_string)


def create(conn):
    with open(DB_SCHEMA_FILENAME) as schema_file:
        schema = schema_file.read()
        conn.cursor().execute(schema)
        conn.commit()


def insert_raw_xml(raw_xml, conn):
    cursor = conn.cursor()
    cursor.execute(RESPONSE_INSERT_QUERY, (raw_xml,))
    response_id = int(cursor.fetchone()[0])
    conn.commit()
    return response_id


def insert_arrivals(response_id, bus_arrivals, conn):
    cursor = conn.cursor()
    columns = siri_parser.monitored_stop_visit_fields + ['response_id']
    for arrival in bus_arrivals:
        values = tuple(list(arrival) + [response_id])
        insert_statement = 'insert into siri_arrivals (%s) values %s'
        cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
    conn.commit()

import psycopg2
import os

ARRIVAL_INSERT_QUERY = """ INSERT INTO arrivals 
				   (line_ref, direction_ref, published_line_name, operator_ref, destination_ref, monitoring_ref, expected_arrival_time, stop_point_ref, response_id) 
				   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
			   """
RESPONSE_INSERT_QUERY = "INSERT INTO responses(response_xml) VALUES(%s) RETURNING id;"
DB_SCHEMA_FILENAME = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "schema.sql")


def connect(**kwargs):
    try:
        conn_string = "dbname={name} user={user} host={host} password={password}".format(
            **kwargs)
        return psycopg2.connect(conn_string)
    except psycopg2.Error:
        print "Unable to connect to database."


def create(conn):
    schema = ""
    with open(DB_SCHEMA_FILENAME) as schema_file:
        schema = schema_file.read()
    conn.cursor().execute(schema)
    conn.commit()


def insert_arrivals(bus_arrivals, conn):
    cursor = conn.cursor()
    for arrival in bus_arrivals:
        response_data = (arrival.response_xml,)
        # print(response_data)
        cursor.execute(RESPONSE_INSERT_QUERY, response_data)
        response_id = int(cursor.fetchone()[0])
        arrival_data = (arrival.line_ref, arrival.direction_ref, arrival.published_line_name, arrival.operator_ref,
                        arrival.destination_ref, arrival.monitoring_ref, arrival.expected_arrival_time, arrival.stop_point_ref, response_id)
        cursor.execute(ARRIVAL_INSERT_QUERY, arrival_data)
    conn.commit()

import sqlite3

DB_FILE_NAME = "static.db"
GET_STOPS_BY_LINE_AND_STATIONS_QUERY = "select distinct stops.stop_code, stops.stop_name, stops.stop_desc " \
                                       "from routes inner join trips on routes.route_id = trips.route_id inner join stop_times " \
                                       "on stop_times.trip_id = trips.trip_id inner join stops on stops.stop_id = stop_times.stop_id " \
                                       "where routes.route_long_name LIKE '%{!s}%<->%{!s}%' and routes.route_short_name = '{!s}'" \
                                       " AND routes.agency_id = '{!s}';"


def select(query, db_file_name=DB_FILE_NAME):
    conn = sqlite3.connect(db_file_name)
    return conn.execute(query)


def get_stations_by_line(line_number, first_station, last_station, operator_id):
    query = GET_STOPS_BY_LINE_AND_STATIONS_QUERY.format(first_station, last_station, line_number, operator_id)
   
    cursor = select(query)
    rows = cursor.fetchall()

    stations = [int(cols[0]) for cols in rows]

    return stations

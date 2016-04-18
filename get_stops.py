from db_insert import select


def get_stations_by_line(line_number, first_station, last_station):
    query = "select distinct stops.stop_code, stops.stop_name, stops.stop_desc " \
            "from routes inner join trips on routes.route_id = trips.route_id inner join stop_times " \
            "on stop_times.trip_id = trips.trip_id inner join stops on stops.stop_id = stop_times.stop_id " \
            "where routes.route_long_name LIKE '%{!s}%<->%{!s}%' and routes.route_short_name = '{!s}';"\
        .format(first_station, last_station, line_number)
    return select(query)
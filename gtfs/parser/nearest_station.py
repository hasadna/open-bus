from gtfs.bus2train.geo import GeoPoint

import psycopg2
import logging
import sys
from configparser import ConfigParser

def parse_config(config_file_name):
    with open(config_file_name) as f:
        # add section header because config parser requires it
        config_file_content = '[Section]\n' + f.read()
    config = ConfigParser()
    config.read_string(config_file_content)
    return {k: v for (k, v) in config['Section'].items()}

def find_nearest_station(cursor):
    logging.debug("Find nearest station starts ")
    query = """SELECT DISTINCT(stops.stop_id), stops.stop_lat, stops.stop_lon FROM routes
    JOIN trips ON trips.route_id = routes.route_id
    JOIN trip_route_story ON trips.trip_id = trip_route_story.trip_id
    JOIN route_story_stops ON route_story_stops.route_story_id = trip_route_story.route_story_id
    JOIN stops ON route_story_stops.stop_id = stops.stop_id WHERE route_type=2 ;"""
    cursor.execute(query)
    stations = {r[0]: GeoPoint(r[1], r[2]) for r in cursor}
    logging.debug("There are %d train stations" % len(stations))

    def nearest_station(stop_point):
        distance_and_stop = {train_station_point.distance_to(stop_point): train_station for
                             train_station, train_station_point in stations.items()}
        min_distance = min(distance_and_stop)
        min_station = distance_and_stop[min_distance]
        return min_distance, min_station

    cursor.execute("SELECT stop_id, stop_lat, stop_lon FROM stops;")
    logging.debug("Finding nearest train station")
    return {r[0]: nearest_station(GeoPoint(r[1], r[2])) for r in cursor}


def update_stops_table(config):
    template = "dbname={d[db_name]} user={d[db_user]} host={d[db_host]} password={d[db_password]}"
    connection_str = template.format(d=config)
    logging.debug("Connection to db with connection string %s" % connection_str )
    connection = psycopg2.connect(connection_str)
    connection.autocommit = True
    cursor = connection.cursor()
    rows = [{'stop_id': key, 'station_distance': int(value[0]), 'station_id': value[1]}
            for key, value in find_nearest_station(cursor).items()]
    logging.debug("Altering stops table: adding nearest_station and station_distance fields")
    try:
        cursor.execute('ALTER TABLE stops ADD COLUMN nearest_train_station INTEGER;')
    except psycopg2.ProgrammingError as e:
        logging.warning(e)
    try:
        cursor.execute('ALTER TABLE stops ADD COLUMN train_station_distance INTEGER;')
    except psycopg2.ProgrammingError as e:
        logging.warning(e)
    logging.debug("Executing update query on stops table")
    cursor.executemany('''UPDATE stops SET nearest_train_station = %(station_id)s,
                          train_station_distance = %(station_distance)s
                          WHERE stop_id=%(stop_id)s;''', rows)
    logging.debug("Closing connection")
    connection.close()
    logging.debug("Done.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout)])
    update_stops_table(parse_config(sys.argv[1]))


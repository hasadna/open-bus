import os
import csv
from sys import argv
from configparser import ConfigParser
from collections import namedtuple

from siri import arrivals, siri_parser

try:
    from siri import db
except ImportError as e:
    print("Error importing siri.db", e)
    print("DB functionality will not work")


def parse_config(config_file_name):
    with open(config_file_name) as f:
        # add section header because config parser requires it
        config_file_content = '[Section]\n' + f.read()
    config = ConfigParser()
    config.read_string(config_file_content)
    string_keys = ["siri_user", "db_host", "db_port", "db_name", "db_user", "db_password", "stops_file",
                   "proxy_url", "output_filename"]
    bool_keys = ["use_proxy", "write_results_to_file"]
    config_dict = {k: config['Section'][k] for k in string_keys}
    # parse booleans manually
    for key in bool_keys:
        value = config['Section'][key].lower()
        if value != 'true' and value != 'false':
            raise Exception('Configuration error: value for key %s should be True or False' % key)
        config_dict[key] = True if value == 'true' else False
    # the code expects an object and not a dictionary (so you can do args.siri_user, rather than args['siri_user'])
    return namedtuple('Args', string_keys + bool_keys)(**config_dict)


def fetch_and_store_arrivals(args, stops):
    if args.write_results_to_file:
        print("Running fetch_arrivals and writing results to file %s" % args.output_filename)
        write_arrivals_to_file(fetch_arrivals(args, stops), args.output_filename)
    else:
        connection_details = {
            "name": args.db_name,
            "user": args.db_user,
            "password": args.db_password,
            "host": args.db_host,
            "port": args.db_port
        }
        conn = db.connect(**connection_details)
        print("Running fetch_arrivals and writing results to DB")
        db.insert_arrivals(fetch_arrivals(args, stops), conn)
        print("Successfully inserted data")


def write_arrivals_to_file(bus_arrivals, filename):
    fieldnames = ["line_ref", "direction_ref", "published_line_name", "operator_ref", "destination_ref",
                  "monitoring_ref", "expected_arrival_time", "stop_point_ref", "response_timestamp", "recorded_at"]
    with open(filename, 'w', encoding='utf8') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(fieldnames)
        for arrival in bus_arrivals:
            arrival_data = (arrival.line_ref, arrival.direction_ref, arrival.published_line_name,
                            arrival.operator_ref,
                            arrival.destination_ref, arrival.monitoring_ref, arrival.expected_arrival_time,
                            arrival.stop_point_ref, arrival.response_timestamp, arrival.recorded_at)
            writer.writerow(arrival_data)


def fetch_arrivals(args, stops):
    request_xml = arrivals.get_arrivals_request_xml(stops, args.siri_user)
    response_xml = arrivals.get_arrivals_response_xml(request_xml, args.use_proxy, args.proxy_url)
    if "User authentication failed".encode('utf-8') in response_xml:
        raise Exception("Error connecting to SIRI: user authentication failed")
    parsed_arrivals = siri_parser.parse_siri_xml(response_xml)
    print("%d arrivals parsed" % len(parsed_arrivals))
    return parsed_arrivals


def get_stops(stops_file):
    with open(stops_file) as stops:
        return [r['stop_code'] for r in  csv.DictReader(stops)]


def main():
    if len(argv) < 2:
        print("Usage: %s config_file_name" % os.path.basename(__file__))
        print("See siri/data/fetch_and_store_arrivals.config.example for a template for the configuration file")
        return
    args = parse_config(argv[1])
    stops = get_stops(args.stops_file)
    print("Querying %d stops" % len(stops))
    fetch_and_store_arrivals(args, stops)


if __name__ == '__main__':
    main()

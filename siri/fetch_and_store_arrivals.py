import argparse
from siri import arrivals, siri_parser
import csv

try:
    from siri import db
except ImportError as e:
    print("Error importing siri.db", e)
    print("DB functionality will not work")


def parse_flags():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_host", type=str,
                        default="localhost",
                        help="Openbus project DB host")
    parser.add_argument("--db_port", type=str,
                        default="5432",
                        help="Openbus project DB port")
    parser.add_argument("--db_name", type=str,
                        default="siri",
                        help="Openbus project DB name")
    parser.add_argument("--db_user", type=str,  help="Openbus project DB user")
    parser.add_argument("--db_password", type=str,  help="Openbus project DB password")
    parser.add_argument("--stops_file", type=str,
                        help="List of stops to query about, space separated.")
    parser.add_argument('--use_proxy', type=bool, default=False,
                        help="Whether to use Open Train server as proxy")
    parser.add_argument("--use_file", type=bool,
                        help="Write the results into a flat file and not DB.")
    parser.add_argument('--output_filename', type=str, default="siri_arrivals.csv",
                        help="If use file is True, specifies file name.")
    return parser.parse_args()


def fetch_and_store_arrivals(args, stops):
    if args.use_file:
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
        db.insert_arrivals(fetch_arrivals(args, stops), conn)
        print("Successfully inserted data")


def write_arrivals_to_file(bus_arrivals, filename):
    fieldnames = ["line_ref", "direction_ref", "published_line_name", "operator_ref", "destination_ref",
                  "monitoring_ref", "expected_arrival_time", "stop_point_ref", "response_timestamp", "recorded_at"]
    with open(filename, 'w', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames, lineterminator='\n')
        writer.writeheader()
        for arrival in bus_arrivals:
            arrival_data = (arrival.line_ref, arrival.direction_ref, arrival.published_line_name,
                            arrival.operator_ref,
                            arrival.destination_ref, arrival.monitoring_ref, arrival.expected_arrival_time,
                            arrival.stop_point_ref, arrival.response_timestamp, arrival.recorded_at)
            writer.writerow(arrival_data)


def fetch_arrivals(args, stops):
    request_xml = arrivals.get_arrivals_request_xml(stops)
    response_xml = arrivals.get_arrivals_response_xml(request_xml, args.use_proxy)
    if "User authentication failed".encode('utf-8') in response_xml:
        raise Exception("Error connecting to SIRI: user authentication failed")
    parsed_arrivals = siri_parser.parse_siri_xml(response_xml)
    print("%d arrivals parsed" % len(parsed_arrivals))
    return parsed_arrivals


def get_stops(stops_file):
    with open(stops_file) as stops:
        return stops.read().split()


def main():
    args = parse_flags()
    stops = get_stops(args.stops_file)
    fetch_and_store_arrivals(args, stops)


if __name__ == '__main__':
    main()

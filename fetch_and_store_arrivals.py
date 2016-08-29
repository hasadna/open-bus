# TODO: fetch all stops from gtfs using get_stops
# TODO: allow querying with custom time ranges

import argparse
from core import arrivals, siri_parser, db


def parse_flags():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_host", type=str,
                        default="localhost",
                        help="Openbus project DB host")
    parser.add_argument("--db_port", type=str,
                        default="5432",
                        help="Openbus project DB port")
    parser.add_argument("--db_name", type=str,
                        default="openbus",
                        help="Openbus project DB name")
    parser.add_argument("--db_user", type=str,
                        help="Openbus project DB user")
    parser.add_argument("--db_password", type=str,
                        help="Openbus project DB password")
    parser.add_argument("--stops", type=str, nargs='+',  # non-empty list
                        default="41207",
                        help="List of stops to query about, space separated.")
    return parser.parse_args()


def fetch_and_store_arrivals(connection_details, stops):
    request_xml = arrivals.get_arrivals_request_xml(stops)
    response_xml = arrivals.get_arrivals_response_xml(request_xml)
    parsed_arrivals = siri_parser.parse_siri_xml(response_xml)
    db.insert_arrivals(parsed_arrivals, db.connect(**connection_details))
    print("Successfully inserted data")


def main():
    args = parse_flags()
    conn = {
        "name": args.db_name,
        "user": args.db_user,
        "password": args.db_password,
        "host": args.db_host,
        "port": args.db_port
    }
    fetch_and_store_arrivals(connection_details=conn, stops=args.stops)

if __name__ == '__main__':
    main()

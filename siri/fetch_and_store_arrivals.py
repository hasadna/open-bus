
import argparse
import arrivals, siri_parser, db, time


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
    parser.add_argument("--db_user", type=str, required=True,
                        help="Openbus project DB user")
    parser.add_argument("--db_password", type=str, required=True,
                        help="Openbus project DB password")
    parser.add_argument("--stops_file", type=str,
                        help="List of stops to query about, space separated.")
    parser.add_argument('--use_proxy', type=bool, default=False,
                        help="Whether to use Open Train server as proxy")
    return parser.parse_args()


# def dump_response_to_file(r):
#     with open("/tmp/siri_response_%s" % time.strftime("%Y%m%d-%H%M%S"), 'wb') as f:
#         f.write(r)


def fetch_and_store_arrivals(connection_details, stops, use_proxy=False):
    conn = db.connect(**connection_details)
    request_xml = arrivals.get_arrivals_request_xml(stops)
    response_xml = arrivals.get_arrivals_response_xml(request_xml, use_proxy)
    if "User authentication failed".encode('utf-8') in response_xml:
        raise Exception("Error connecting to SIRI: user authentication failed")
    # dump_response_to_file(response_xml)
    parsed_arrivals = siri_parser.parse_siri_xml(response_xml)
    print("%d arrivals parsed" % len(parsed_arrivals))
    db.insert_arrivals(parsed_arrivals, conn)
    print("Successfully inserted data")


def get_stops(stops_file):
    with open(stops_file) as stops:
        return stops.read().split()


def main():
    args = parse_flags()
    conn = {
        "name": args.db_name,
        "user": args.db_user,
        "password": args.db_password,
        "host": args.db_host,
        "port": args.db_port
    }
    stops = get_stops(args.stops_file)
    fetch_and_store_arrivals(connection_details=conn, stops=stops, use_proxy=args.use_proxy)


if __name__ == '__main__':
    main()

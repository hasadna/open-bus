from core import arrivals, siri_parser, db

# TODO: remove mock data and use gtfs stops instead
stops = """
41207
""".splitlines()

CONNECTION_DETAILS = {
    "name": "openbus",
    "user": "openbus",
    "password": "openbus",
    "host": "localhost",
    "port": "5432"
}

def main():
    # TODO: fetch all stops from gtfs using get_stops
    request_xml = arrivals.get_arrivals_request_xml(stops)
    response_xml = arrivals.get_arrivals_response_xml(request_xml)
    parsed_arrivals = siri_parser.parse_siri_xml(response_xml)
    db.insert_arrivals(parsed_arrivals, db.connect(**CONNECTION_DETAILS))
    print("Successfully inserted")
if __name__ == '__main__':
    main()

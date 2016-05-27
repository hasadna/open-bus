from core import arrivals, siri_parser, db

# TODO: remove mock data and use gtfs stops instead
stops = """
26472
26466
26465
28577
26222
21320
21182
21614
26174
26172
26166
28580
26094
26087
21284
25749
25746
25744
21134
26042
21595
26035
25695
25740
21587
21422
21237
21243
25604
25621
25607
25609
26932
25779
20364
25812
25832
25840
27246
25867""".splitlines()

CONNECTION_DETAILS = {
    "name": "openbus",
    "user": "openbus",
    "password": "openbus",
    "host": "localhost"
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

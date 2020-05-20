import json
import os
import unittest
from datetime import datetime
from jsonschema import validate, FormatChecker, ValidationError, SchemaError

from data_stream.base_classes import SiriRide, SiriRecord, GeoPoint


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', "schema.json")) as f:
            cls.schema = json.load(f)
        # validate that strict_rfc3339 module could be imported. in case this module is not installed the validation of
        # date/time formats will return false positive

        # noinspection PyUnresolvedReferences
        import strict_rfc3339

    def test_to_json_returns_valid_dict(self):
        instance = SiriRide(siri_ride_id=6, line_name='25a', license_plate=1234567, operator_ref=4, line_ref=456,
                            departure_time=datetime.now(), journey_ref=234,
                            siri_records=[SiriRecord(recorded_at=datetime.now().time(),
                                                     response_timestamp=datetime.now(),
                                                     expected_arrival_time=datetime.now().time(),
                                                     current_location=GeoPoint(12.12, 23.23))])

        actual = instance.to_json()

        validate(actual, self.schema, format_checker=FormatChecker())

    def test_hardcoded_example_is_valid(self):

        instance = {
              "type": "siri_ride",
              "id": "12",
              "attributes": {
                "lineName": "25B",
                "licensePlate": 234,
                "departureTime": "23:00:00",
                "operatorRef": 4,
                "lineRef": 66554,
                "journeyRef": 77889,
                "siriRecords": [
                  {"recordedAt": "23:09:00",
                   "responseTimestamp": "2013-03-25T12:42:31+00:00",
                   "expectedArrivalTime": "23:17:00",
                   "point": {
                       "type": "Point",
                       "coordinates": [40, 23.2]}},
                  {"recordedAt": "23:09:00",
                   "responseTimestamp": "2013-03-25T12:42:31+00:00",
                   "expectedArrivalTime": "23:17:00",
                   "point": {
                         "type": "Point",
                         "coordinates": [40, 23.2]}}
                ]
              }
        }

        try:
            validate(instance, self.schema, format_checker=FormatChecker())

        except (ValidationError, SchemaError):
            self.fail("validate() raised Exception unexpectedly!")


if __name__ == '__main__':
    unittest.main()

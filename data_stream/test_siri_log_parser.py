import io
import unittest
import datetime
import os
from data_stream.base_classes import SiriRide, SiriRecord, GeoPoint
from data_stream.siri_log_parser import InMemoryRidesCacheMechanism, SiriLogParser


class TestInMemoryRidesCacheMechanism(unittest.TestCase):

    def setUp(self) -> None:
        self.ride = SiriRide(line_name='290', license_plate='5596287', operator_ref=18, line_ref=10583,
                             departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records=[
                                SiriRecord(recorded_at=datetime.time(23, 9, 33),
                                           response_timestamp=datetime.datetime(2020, 6, 24, 23, 11, 30),
                                           expected_arrival_time=datetime.time(23, 34), current_location=GeoPoint(
                                        longitude=31.712017, latitude=35.17242))])

        self.updated_ride = SiriRide(line_name='290', license_plate='5596287', operator_ref=18, line_ref=10583,
                                     departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records=[
                                      SiriRecord(recorded_at=datetime.time(23, 9, 33),
                                                 response_timestamp=datetime.datetime(2020, 6, 24, 23, 11, 30),
                                                 expected_arrival_time=datetime.time(23, 34), current_location=GeoPoint(
                                              longitude=31.712017, latitude=35.17242)),
                                      SiriRecord(recorded_at=datetime.time(23, 11, 33),
                                                 response_timestamp=datetime.datetime(2020, 6, 24, 23, 12, 45),
                                                 expected_arrival_time=datetime.time(23, 34), current_location=GeoPoint(
                                              longitude=32.34, latitude=36.65))])

    def test_calling_add_record_and_get_record_returns_same_record(self):

        rides_data = InMemoryRidesCacheMechanism()

        rides_data.add_ride(self.ride)

        actual = next(rides_data.get_rides())

        self.assertEqual(self.ride, actual)

    def test_calling_add_record_and_get_record_returns_last_record(self):

        rides_data = InMemoryRidesCacheMechanism()

        rides_data.add_ride(self.ride)
        rides_data.add_ride(self.updated_ride)

        actual = next(rides_data.get_rides())

        self.assertEqual(self.updated_ride, actual)


class TestSiriLogParserIntegration(unittest.TestCase):

    def setUp(self) -> None:
        self.parser = SiriLogParser(InMemoryRidesCacheMechanism())

    def test_parse_csv_file(self):
        # Arrange
        expected = SiriRide(line_name='290', license_plate='5596287', operator_ref=18, line_ref=10583,
                            departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records=[
                                SiriRecord(recorded_at=datetime.time(23, 9, 33),
                                           response_timestamp=datetime.datetime(2020, 6, 24, 23, 11, 30),
                                           expected_arrival_time=datetime.time(23, 34), current_location=GeoPoint(
                                            longitude=31.712017, latitude=35.17242))])

        f = io.StringIO("2020-06-24T23:11:30,[line 290 v 5596287 oad 22:40 ea 23:34],18,10583,290,47405958,2020-06-24T"
                        "22:40:00,5596287,2020-06-24T23:34:00,2020-06-24T23:09:33,31.712017,35.17242,2020-06-24,9807,2"
                        ",v2")
        parser = SiriLogParser(InMemoryRidesCacheMechanism())

        # Act
        parser.parse_csv_file(f)
        actual = next(parser.get_rides())

        # Assert
        self.assertEqual(expected, actual)

    def test_parse_gz_file(self):
        # Arrange
        log_file_1 = os.path.join(os.path.dirname(__file__), 'test_assets', 'siri_rt_data_v2.2020-06-24.1_min.log.gz')

        # Act
        self.parser.parse_gz_file(log_file_1)
        actual_quantity_of_rides = len(list(self.parser.get_rides()))

        # Assert
        expected_quantity_of_rides = 75
        self.assertEqual(expected_quantity_of_rides, actual_quantity_of_rides)

    def test_parse_multi_gz_files(self):
        # Arrange
        log_file_1 = os.path.join(os.path.dirname(__file__), 'test_assets', 'siri_rt_data_v2.2020-06-24.1_min.log.gz')
        log_file_2 = os.path.join(os.path.dirname(__file__), 'test_assets', 'siri_rt_data_v2.2020-06-25.0_min.log.gz')


        # Act
        self.parser.parse_multi_gz_files([log_file_1, log_file_2])
        actual_quantity_of_rides = len(list(self.parser.get_rides()))

        # Assert
        expected_quantity_of_rides = 156
        self.assertEqual(expected_quantity_of_rides, actual_quantity_of_rides)


if __name__ == '__main__':
    unittest.main()

import io
import sqlite3
import unittest
import datetime
import os
from unittest.mock import MagicMock

from data_stream.base_classes import SiriRide, SiriRecord, GeoPoint
from data_stream.siri_log_parser import InMemoryRidesCacheMechanism, SiriLogParser, SqliteRidesCacheMechanism


class TestSqliteRidesCacheMechanismUnitTests(unittest.TestCase):

    DB_FILE = 'example4.db'

    def tearDown(self) -> None:
        if os.path.isfile(self.DB_FILE):
            os.remove(self.DB_FILE)

    def test_add_ride_with_one_record(self):

        # Prepare
        record = SiriRide(line_name='290', license_plate='5596287', operator_ref=18, line_ref=10583,
                          departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records={
                            SiriRecord(recorded_at=datetime.time(23, 9, 33),
                                       response_timestamp=datetime.datetime(2020, 6, 24, 23, 11, 30),
                                       expected_arrival_time=datetime.time(23, 34), current_location=GeoPoint(
                                    longitude=31.712017, latitude=35.17242))})
        conn = sqlite3.connect(self.DB_FILE)
        d = SqliteRidesCacheMechanism(conn)

        # Act
        d.add_ride(record)
        actual = next(d.get_rides())

        # Assert
        self.assertEqual(record, actual)

    def test_add_ride_with_two_record(self):

        siri_record_1 = SiriRecord(recorded_at=datetime.time(23, 9, 33),
                                   response_timestamp=datetime.datetime(2020, 6, 24, 23, 11, 30),
                                   expected_arrival_time=datetime.time(23, 34), current_location=GeoPoint(
                longitude=31.712017, latitude=35.17242))

        siri_record_2 = SiriRecord(recorded_at=datetime.time(23, 11, 00),
                                   response_timestamp=datetime.datetime(2020, 6, 24, 23, 12, 30),
                                   expected_arrival_time=datetime.time(23, 35), current_location=GeoPoint(
                                    longitude=33.712017, latitude=37.17242))

        ride_1 = SiriRide(line_name='290', license_plate='5596287', operator_ref=18, line_ref=10583,
                          departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records={siri_record_1})
        ride_2 = SiriRide(line_name='290', license_plate='5596287', operator_ref=18, line_ref=10583,
                          departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records={siri_record_2})
        ride_combined = SiriRide(line_name='290', license_plate='5596287', operator_ref=18, line_ref=10583,
                                 departure_time=datetime.time(22, 40), journey_ref=47405958,
                                 siri_records={siri_record_1, siri_record_2})

        conn = sqlite3.connect(self.DB_FILE)
        d = SqliteRidesCacheMechanism(conn)

        # Act
        d.add_ride(ride_1)
        d.add_ride(ride_2)
        actual = next(d.get_rides())

        # Assert
        self.assertEqual(ride_combined, actual)

    def test_add_two_rides(self):
        # Prepare
        record = SiriRide(line_name='290', license_plate='5596287', operator_ref=18, line_ref=10583,
                          departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records={
                            SiriRecord(recorded_at=datetime.time(23, 9, 33),
                                       response_timestamp=datetime.datetime(2020, 6, 24, 23, 11, 30),
                                       expected_arrival_time=datetime.time(23, 34), current_location=GeoPoint(
                                    longitude=31.712017, latitude=35.17242))})

        another_record = SiriRide(line_name='100', license_plate='9996287', operator_ref=18, line_ref=10583,
                                  departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records={
                                    SiriRecord(recorded_at=datetime.time(23, 9, 33),
                                               response_timestamp=datetime.datetime(2020, 6, 24, 23, 11, 30),
                                               expected_arrival_time=datetime.time(23, 34), current_location=GeoPoint(
                                            longitude=31.712017, latitude=35.17242))})

        conn = sqlite3.connect(self.DB_FILE)
        d = SqliteRidesCacheMechanism(conn)

        # Act
        d.add_ride(record)
        d.add_ride(another_record)

        actual = set(d.get_rides())
        expected = {record, another_record}

        # Assert
        self.assertEqual(2, len(actual))
        self.assertEqual(expected, actual)

    def test_commit(self):
        # Arrange
        mock = MagicMock()
        t = SqliteRidesCacheMechanism(mock)

        # Act
        t.commit()

        # Assert
        mock.commit.assert_called_with()

    def test_close(self):
        # Arrange
        mock = MagicMock()
        t = SqliteRidesCacheMechanism(mock)

        # Act
        t.close()

        # Assert
        mock.close.assert_called_with()


class TestInMemoryRidesCacheMechanism(unittest.TestCase):

    def setUp(self) -> None:
        self.ride = SiriRide(line_name='290', license_plate='5596287', operator_ref=18, line_ref=10583,
                             departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records={
                                SiriRecord(recorded_at=datetime.time(23, 9, 33),
                                           response_timestamp=datetime.datetime(2020, 6, 24, 23, 11, 30),
                                           expected_arrival_time=datetime.time(23, 34), current_location=GeoPoint(
                                        longitude=31.712017, latitude=35.17242))})

        self.updated_ride = SiriRide(line_name='290', license_plate='5596287', operator_ref=18, line_ref=10583,
                                     departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records={
                                        SiriRecord(recorded_at=datetime.time(23, 9, 33),
                                                   response_timestamp=datetime.datetime(2020, 6, 24, 23, 11, 30),
                                                   expected_arrival_time=datetime.time(23, 34),
                                                   current_location=GeoPoint(longitude=31.712017, latitude=35.17242)),
                                        SiriRecord(recorded_at=datetime.time(23, 11, 33),
                                                   response_timestamp=datetime.datetime(2020, 6, 24, 23, 12, 45),
                                                   expected_arrival_time=datetime.time(23, 34),
                                                   current_location=GeoPoint(longitude=32.34, latitude=36.65))})

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
                            departure_time=datetime.time(22, 40), journey_ref=47405958, siri_records={
                                SiriRecord(recorded_at=datetime.time(23, 9, 33),
                                           response_timestamp=datetime.datetime(2020, 6, 24, 23, 11, 30),
                                           expected_arrival_time=datetime.time(23, 34), current_location=GeoPoint(
                                        longitude=31.712017, latitude=35.17242))})

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

    def test_parse_multi_gz_files_sqlite(self):
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

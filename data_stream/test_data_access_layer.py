import unittest
from datetime import datetime
from pymongo import MongoClient

from data_stream.base_classes import SiriRide, SiriRecord, GeoPoint
from data_stream.data_access_layer import FilterError, MongoCrud, SiriRideMongoCrud, AlreadyExist


class TestSiriRideMongoCrud(unittest.TestCase):
    database_name = 'my_db_name'
    collection_name = 'coll_name'

    def setUp(self) -> None:
        MongoClient().drop_database(self.database_name)
        self.crud = SiriRideMongoCrud(MongoCrud(MongoClient(), self.database_name))

    def test_create_with_doc_id_raise_AlreadyExist_exception(self):
        ride = SiriRide(doc_id="FOO", line_name='25a', license_plate='1234567', operator_ref=4, line_ref=456,
                        departure_time=datetime.now().time(), journey_ref=234, siri_records=[
                         SiriRecord(recorded_at=datetime.now().time(), response_timestamp=datetime.now(),
                                    expected_arrival_time=datetime.now().time(),
                                    current_location=GeoPoint(12.12, 23.23))])
        with self.assertRaises(AlreadyExist):
            self.crud.create(ride)

    def test_create_and_read(self):
        ride = SiriRide(line_name='25a', license_plate='1234567', operator_ref=4, line_ref=456,
                        departure_time=datetime.now().time(), journey_ref=234, siri_records=[
                         SiriRecord(recorded_at=datetime.now().time(), response_timestamp=datetime.now(),
                                    expected_arrival_time=datetime.now().time(),
                                    current_location=GeoPoint(12.12, 23.23))])

        doc_id = self.crud.create(ride)

        actual = self.crud.read(doc_id).to_json()

        self.assertEqual(ride.to_json(), actual)

    def test_create_update_and_read(self):
        # Arrange
        ride = SiriRide(line_name='25a', license_plate='1234567', operator_ref=4, line_ref=456,
                        departure_time=datetime.now().time(), journey_ref=234, siri_records=[
                         SiriRecord(recorded_at=datetime.now().time(), response_timestamp=datetime.now(),
                                    expected_arrival_time=datetime.now().time(),
                                    current_location=GeoPoint(12.12, 23.23))])

        # Act
        doc_id = self.crud.create(ride)
        ride.line_name = 77
        self.crud.update(ride)
        actual = self.crud.read(doc_id).to_json()

        # Assert
        self.assertEqual(ride.to_json(), actual)

    def test_find(self):
        # Arrange
        ride_1 = SiriRide(line_name='25a', license_plate='1234567', operator_ref=4, line_ref=456,
                          departure_time=datetime.now().time(), journey_ref=234, siri_records=[
                            SiriRecord(recorded_at=datetime.now().time(), response_timestamp=datetime.now(),
                                       expected_arrival_time=datetime.now().time(),
                                       current_location=GeoPoint(12.12, 23.23))])

        ride_2 = SiriRide(line_name='4', license_plate='1234567', operator_ref=4, line_ref=456,
                          departure_time=datetime.now().time(), journey_ref=678, siri_records=[
                            SiriRecord(recorded_at=datetime.now().time(), response_timestamp=datetime.now(),
                                       expected_arrival_time=datetime.now().time(),
                                       current_location=GeoPoint(42.12, 26.23))])
        expected = [ride_1, ride_2]
        self.crud.create(ride_1)
        self.crud.create(ride_2)

        # Act
        actual = list(self.crud.find(filter=dict(type="siri_ride")))

        # Assert
        self.assertEqual(expected, actual)


class TestMongo(unittest.TestCase):
    database_name = 'my_db_name'
    collection_name = 'coll_name'

    def setUp(self) -> None:
        MongoClient().drop_database(self.database_name)
        self.crud = MongoCrud(MongoClient(), self.database_name)

    def test_basic_flow_of_create_update_and_read_operations(self):
        # Arrange
        doc = dict(doc_type='siri_ride', attributes=dict(foo='bar'))

        # Act
        doc_id = self.crud.create(self.collection_name, doc)
        doc['attributes']['foo'] = 'vaz'

        self.crud.update(self.collection_name, dict(_id=doc_id), doc)
        actual = self.crud.read(self.collection_name, dict(_id=doc_id))

        # Assert
        self.assertEqual(doc, actual)

    def test_find(self):
        doc_1 = dict(doc_type='siri_ride', attributes=dict(foo='bar'))
        doc_2 = dict(doc_type='siri_ride', attributes=dict(foo='vaz'))
        self.crud.create(self.collection_name, doc_1)
        self.crud.create(self.collection_name, doc_2)

        actual = self.crud.find(self.collection_name, filter=dict(doc_type='siri_ride'))

        self.assertEqual(list(actual), [doc_1, doc_2])

    def test_update_with_filter_that_not_matched_raise_value_error(self):
        with self.assertRaises(FilterError):
            self.crud.update(self.collection_name, dict(foo='bar'), {'bar': 'vaz'})

    def test_read_with_filter_that_not_matched_raise_value_error(self):
        with self.assertRaises(FilterError):
            self.crud.read(self.collection_name, dict(foo='bar'))


if __name__ == '__main__':
    unittest.main()

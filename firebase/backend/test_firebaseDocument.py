from datetime import datetime
from unittest import TestCase

from firebase_documents import FirebaseDocument, SiriRide, SiriPoint, Point


class TestFirebaseDocument(TestCase):
    def test_to_firebase_dict(self):
        self.assertRaises(NotImplementedError, FirebaseDocument().to_firebase_dict)


class TestSiriRide(TestCase):
    def test__init__(self):
        SiriRide(route_id=1001, agency_id=5, bus_id='23456', planned_start_datetime=datetime.fromtimestamp(1),
                 route_short_name='None', stop_point_ref=(1.1, 2.2), trip_id_to_date=57434, points=[], foo=4)

    def test_to_firebase_dict(self):

        first_point = SiriPoint(rec_dt=datetime.fromtimestamp(1), pred_dt=datetime.fromtimestamp(1),
                                point=Point(1.1, 2.2))

        actual = SiriRide(route_id=1001, agency_id=5, bus_id='23456', planned_start_datetime=datetime.fromtimestamp(1),
                          route_short_name='None', stop_point_ref=(1.1, 2.2), trip_id_to_date=57434,
                          points=[first_point], foo=4).to_firebase_dict()

        expected = dict(route_id=1001,
                        agency_id=5,
                        bus_id='23456',
                        planned_start_datetime=datetime.fromtimestamp(1),
                        route_short_name='None',
                        stop_point_ref=(1.1, 2.2),
                        trip_id_to_date=57434,
                        points=[first_point.to_firebase_dict()],
                        metadata=dict(foo=4))

        self.assertEqual(expected, actual)


class TestSiriPoint(TestCase):
    def test_from_str(self):
        # Prepare
        argument = "2019-01-01T14:00:00|1.1|2.2|2019-01-01T14:01:00"
        rec_dt, lat, lon, pred_dt = argument.split('|')

        # Execute
        actual = SiriPoint.from_str(argument)

        # Test
        self.assertEqual(datetime.strptime(rec_dt, '%Y-%m-%dT%H:%M:%S'), actual.rec_dt)
        self.assertEqual(datetime.strptime(pred_dt, '%Y-%m-%dT%H:%M:%S'), actual.pred_dt)
        self.assertEqual(float(lat), actual.point.lat)
        self.assertEqual(float(lon), actual.point.lon)

    def test_to_firebase_dict(self):
        # Expected
        expected_point = Point(1.1, 2.2)
        expected_rec_dt = datetime.strptime('2019-01-01T14:00:00', '%Y-%m-%dT%H:%M:%S')
        expected_pred_dt = datetime.strptime('2019-01-01T15:00:00', '%Y-%m-%dT%H:%M:%S')
        expected = dict(point=expected_point.to_firebase_dict(), pred_dt=expected_pred_dt, rec_dt=expected_rec_dt)

        # Prepare
        actual = SiriPoint(point=expected_point, rec_dt=expected_rec_dt, pred_dt=expected_pred_dt).to_firebase_dict()

        self.assertEqual(expected, actual)

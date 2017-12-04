import datetime
import unittest

import psycopg2

import crud_stub
import RealTimeArrivals


class MyTestCase(unittest.TestCase):
    def test_init_stop(self):
        # prepare
        args = {'route_id': 10802,
                'route_long_name': 'כניסה ראשית/הדסה עין כרם-ירושלים<->האוניברסיטה העברית הר הצופים-ירושלים-1א',
                'trip_id': '24104916_010117', 'stop_sequence': 1, 'stop_id': 9863, 'route_short_name': '19',
                'shape_dist_traveled': 0, 'arrival_time': '18:15:00'}
        # exec
        stop = RealTimeArrivals.Stop(**args)
        # test
        self.assertEqual(stop.route_id, args['route_id'])
        self.assertEqual(stop.trip_id, args['trip_id'])
        self.assertEqual(stop.stop_sequence, args['stop_sequence'])
        self.assertEqual(stop.stop_id, args['stop_id'])
        self.assertEqual(stop.route_id, args['route_id'])
        self.assertEqual(stop.shape_dist_traveled, args['shape_dist_traveled'])

    def test_init_record(self):
        # prepare
        args = {'vehicle_ref': '8761901', 'trip_id': '24104916_010117',
                'recorded_at_time': datetime.datetime(2017, 2, 2, 16, 35, 48,
                                                      tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'route_offset': 0.362768825871595}
        # exec
        record = RealTimeArrivals.Record(**args)
        self.assertEqual(record.vehicle_ref, args['vehicle_ref'])
        self.assertEqual(record.trip_id, args['trip_id'])
        self.assertEqual(record.recorded_at_time, args['recorded_at_time'])
        self.assertEqual(record.route_offset, args['route_offset'])

    def test_init_trip(self):
        # prepare
        args = dict(trip_id='24104916_010117', trip_date=datetime.date(2017, 2, 2))
        # exec
        trip = RealTimeArrivals.Trip(**args)
        # test
        self.assertEqual(trip.trip_date, args['trip_date'])
        self.assertEqual(trip.trip_id, args['trip_id'])

    def test_trip_fill_sort_stops(self):
        # prepare
        args = dict(trip_id='24104916_010117', trip_date=datetime.date(2017, 2, 2))
        trip = RealTimeArrivals.Trip(crud =crud_stub.CrudStub(), **args)
        # exec
        trip._fill_()
        for num, stop in enumerate(trip.stops[1:]):
            curr = stop.stop_sequence
            prev = trip.stops[num].stop_sequence
            self.assertTrue(curr > prev)

    def test_trip_fill_sort_records(self):
        # prepare
        args = dict(trip_id='24104916_010117', trip_date=datetime.date(2017, 2, 2))
        trip = RealTimeArrivals.Trip(crud =crud_stub.CrudStub(), **args)
        # exec
        trip._fill_()
        for num, record in enumerate(trip.records[1:]):
            curr = record.route_offset
            prev = trip.records[num].route_offset
            self.assertTrue(curr > prev)

    def test_trip_fill_set_records(self):
        # prepare
        args = dict(trip_id='24104916_010117', trip_date=datetime.date(2017, 2, 2))
        trip = RealTimeArrivals.Trip(crud =crud_stub.CrudStub(), **args)
        # exec
        trip._fill_()

        expect = len({x['recorded_at_time'] for x in crud_stub.CrudStub.raw_records})

        self.assertEqual(expect, len(trip.records))

    def test_trip_fill_set_route_offset_in_meters(self):
        # prepare
        args = dict(trip_id='24104916_010117', trip_date=datetime.date(2017, 2, 2))
        trip = RealTimeArrivals.Trip(crud =crud_stub.CrudStub(), **args)
        # exec
        trip._fill_()

        for i in trip.records:
            self.assertTrue(i.route_offset_in_meters is not None)

    def test_trip_real_time_without_exception(self):
        # noinspection PyBroadException
        try:
            # prepare
            args = dict(trip_id='24104916_010117', trip_date=datetime.date(2017, 2, 2))
            trip = RealTimeArrivals.Trip(crud =crud_stub.CrudStub(), **args)
            # exec
            trip._fill_()
        except Exception:
            self.fail("exception")


if __name__ == '__main__':
    unittest.main()

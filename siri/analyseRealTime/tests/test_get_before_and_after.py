import datetime
import unittest

import Cruds
import RealTimeArrivals


class StubRecordsBefore(Cruds.Crud):
    def read_records_from_siri(self, trip_id=None, trip_date=None):
        return [RealTimeArrivals.Record(recorded_at_time=datetime.datetime(2017, 1, 1, 12, 30), route_offset=0.4),
                RealTimeArrivals.Record(recorded_at_time=datetime.datetime(2017, 1, 1, 13), route_offset=0.8)]

    def read_stops(self, trip_id=None):
        return [RealTimeArrivals.Stop(stop_sequence=4, shape_dist_traveled=2500)]


class StubRecordsAfter(Cruds.Crud):
    def read_records_from_siri(self, trip_id=None, trip_date=None):
        return [RealTimeArrivals.Record(recorded_at_time=datetime.datetime(2017, 1, 1, 12, 30), route_offset=1.4),
                RealTimeArrivals.Record(recorded_at_time=datetime.datetime(2017, 1, 1, 13), route_offset=1.8)]

    def read_stops(self, trip_id=None):
        return [RealTimeArrivals.Stop(stop_sequence=4, shape_dist_traveled=2500)]


class StubRecordsRegular(Cruds.Crud):
    def read_records_from_siri(self, trip_id=None, trip_date=None):
        return [RealTimeArrivals.Record(recorded_at_time=datetime.datetime(2017, 1, 1, 12, 30), route_offset=0.5),
                RealTimeArrivals.Record(recorded_at_time=datetime.datetime(2017, 1, 1, 13), route_offset=1.5)]

    def read_stops(self, trip_id=None):
        return [RealTimeArrivals.Stop(stop_sequence=4, shape_dist_traveled=1000)]


records = [RealTimeArrivals.Record(recorded_at_time=datetime.datetime(2017, 1, 1, 12), route_offset=0),
           RealTimeArrivals.Record(recorded_at_time=datetime.datetime(2017, 1, 1, 12, 30), route_offset=0.4),
           RealTimeArrivals.Record(recorded_at_time=datetime.datetime(2017, 1, 1, 13), route_offset=0.8)]

stops = [RealTimeArrivals.Stop(stop_sequence=1, shape_dist_traveled=0),
         RealTimeArrivals.Stop(stop_sequence=2, shape_dist_traveled=500),
         RealTimeArrivals.Stop(stop_sequence=3, shape_dist_traveled=1500),
         RealTimeArrivals.Stop(stop_sequence=4, shape_dist_traveled=2500)]


class TestGetBeforeAndAfter(unittest.TestCase):
    def test_stop_between_records(self):
        trip = RealTimeArrivals.Trip()
        trip.records = records[1:]
        trip._add_route_offset_in_meters(stops[-1].shape_dist_traveled)

        bef, aft = trip._get_before_and_after_records(stop=stops[2])
        self.assertEqual(bef, records[1])
        self.assertEqual(aft, records[2])

    def test_stop_before_records(self):
        trip = RealTimeArrivals.Trip()
        trip.records = records[1:]
        trip._add_route_offset_in_meters(1)

        try:
            trip._get_before_and_after_records(stop=stops[1])
        except ValueError:
            return
        self.fail()

    def test_stop_after_records(self):
        trip = RealTimeArrivals.Trip()
        trip.records = records[1:]
        trip._add_route_offset_in_meters(1)

        try:
            trip._get_before_and_after_records(stop=stops[3])
        except ValueError:
            return
        self.fail()

    def test_all_records_BEFORE_stop_get_no_real_time(self):

        # prepare
        trip = RealTimeArrivals.Trip(crud=StubRecordsBefore())

        # exec
        trip._fill_()
        # trip.real_time()
        # test
        self.assertFalse(trip.real_times)

    def test_all_records_AFTER_stop_get_no_real_time(self):

        # prepare
        trip = RealTimeArrivals.Trip(crud=StubRecordsAfter())

        # exec
        trip._fill_()
        # trip.real_time()
        # test
        self.assertFalse(trip.real_times)

    def test_stop_BETWEEN_records_get_real_time(self):

        # prepare
        trip = RealTimeArrivals.Trip(crud=StubRecordsRegular())

        # exec
        trip._fill_()
        # trip.real_time()
        # test
        self.assertTrue(trip.real_times)

        self.assertTrue(trip.real_times[0].real_time == datetime.datetime(2017, 1, 1, 12, 45))
        self.assertTrue(trip.real_times[0].speed == 2.0)


if __name__ == '__main__':
    unittest.main()

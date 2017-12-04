import datetime
import unittest

import ConfigFileParser
import Cruds
from concurrent.futures import ThreadPoolExecutor

import RealTimeArrivals

conn_config = ConfigFileParser.get_connection_parameters('../configurations.config')

class MyTestCase(unittest.TestCase):
    def test_read_gtfs(self):
        # excpect
        excpected_num_elems = 48
        excpected_type_elem = RealTimeArrivals.Stop

        # exec
        with Cruds.Connection(**conn_config) as c:
            crud = Cruds.CrudPostgresql(c)
            data = crud.read_stops('27782048_310717')

        # test num elems
        self.assertEqual(excpected_num_elems, len(data))
        # test type elem
        self.assertTrue(all([isinstance(i, excpected_type_elem) for i in data]))

    def test_read_records(self):
        # excpect
        excpected_num_elems = 1548
        excpected_type_elem = RealTimeArrivals.Record

        # prepare
        with Cruds.Connection(**conn_config) as c:
            crud = Cruds.CrudPostgresql(c)
            data = crud.read_records_from_siri('27782048_310717', datetime.date(2017, 7, 31))

        # test num elems
        self.assertEqual(excpected_num_elems, len(data))
        # test type elem
        self.assertTrue(all([isinstance(i, excpected_type_elem) for i in data]))

    def test_wrire_arrivals(self):
        with Cruds.Connection(**conn_config) as c:
            trip = RealTimeArrivals.Trip(trip_date=datetime.date(2017, 7, 31), trip_id='27782048_310717', crud=Cruds.CrudPostgresql(c))
            trip()

    def test_threadpool(self):
        pool = ThreadPoolExecutor()



        trip_ids = ["27782048_310717", "27782049_310717"]
        with Cruds.Connection(**conn_config) as c:

            trips = [RealTimeArrivals.Trip(trip_date=datetime.date(2017, 7, 31), trip_id= i, crud=Cruds.CrudPostgresql(c))
                     for i in trip_ids]

            futuers = [pool.submit(trip) for trip in trips]

            for i in futuers:
                print (i)
                i.result(120)

if __name__ == '__main__':
    unittest.main()

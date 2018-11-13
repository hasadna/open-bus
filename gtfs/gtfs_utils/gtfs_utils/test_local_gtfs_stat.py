import unittest
from gtfs_utils import local_gtfs_stat
import datetime


class MyTestCase(unittest.TestCase):
    def test_main(self):

        path = '/home/aviv/Downloads/israel-public-transportation_1.zip'
        path_to_tariff = '/home/aviv/Downloads/Tariff.zip'
        date = datetime.date.today()

        local_gtfs_stat.main(path,path_to_tariff,date)


if __name__ == '__main__':
    unittest.main()

import unittest
from gtfs_utils import local_gtfs_stat
import datetime
import tempfile
import pandas as pd


class MyTestCase(unittest.TestCase):

    def test_get_output_path(self):
        output_folder = 'my\\local\\folder'
        file_name = 'foo'
        actual = local_gtfs_stat.get_output_path(datetime.date.today(), output_folder, file_name)

        expected = 'my\\local\\folder'.replace('\\', '/') + '/' + datetime.date.today().strftime('%Y-%m-%d') + '_' + \
                   file_name
        self.assertEqual(expected, actual)

    def test_save_as_pickele(self):
        # Prepare
        with tempfile.TemporaryDirectory() as tmpdirname:
            path = tmpdirname + '/tmp'
            obj = {'foo':'bar'}

            # Execute
            local_gtfs_stat.save_as_pickele(obj,path)

            # Test
            actual = pd.read_pickle(path, compression='gzip')

            self.assertEqual(obj,actual)




if __name__ == '__main__':
    unittest.main()

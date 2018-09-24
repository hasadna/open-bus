import unittest
import gtfs_retrieve_FS
import tempfile
import pickle
import shutil

folder = ''


class MyTestCase(unittest.TestCase):
    def setUp(self):
        global folder
        folder = tempfile.mkdtemp()
        gtfs_retrieve_FS.init(folder)

    def tearDown(self):
        shutil.rmtree(folder)

    def test_init_empty(self):
        with open(gtfs_retrieve_FS.pickle_location, 'rb') as f:
            actual = pickle.load(f)

        expected = {}
        self.assertEqual(expected, actual)

    def test_init_with_data(self):
        # expected
        expected = {'foo': 'bar'}

        # prepare
        # dump new full dict into the pickle
        with open(gtfs_retrieve_FS.pickle_location, 'wb') as f:
            pickle.dump(expected, f)

        # Execute
        gtfs_retrieve_FS.init(folder)
        actual = gtfs_retrieve_FS.obj

        self.assertEqual(actual, expected)

    def test_dump_and_load(self):
        # prepare
        expected = {'foo': 4, 'bar': 5}

        gtfs_retrieve_FS.obj = expected

        gtfs_retrieve_FS._dump_pickle()
        gtfs_retrieve_FS._load_pickle()

        actual = gtfs_retrieve_FS.obj

        self.assertEqual(expected, actual)

    def test_get_empty(self):
        expected = None
        actual = gtfs_retrieve_FS._get('foo')
        self.assertEqual(expected, actual)

    def test_get_added_value(self):
        expected = 'bar'
        gtfs_retrieve_FS._add('foo', expected)

        actual = gtfs_retrieve_FS._get('foo')
        self.assertEqual(actual, expected)

    def test_add_updates_the_pickle(self):
        gtfs_retrieve_FS._add('foo', 'bar')

        with open(gtfs_retrieve_FS.pickle_location, 'rb') as f:
            actual = pickle.load(f)

        expected = {'foo': 'bar'}

        self.assertEqual(actual, expected)

    def test_add_file_metadata(self):
        gtfs_retrieve_FS.add_file_metadata('foo', 'bar', 36003600, 'foobar')

        expected = {'foobar': {'local_filename': 'bar', 'remote_filename': 'foo', 'timestamp_datetime': 36003600}}
        actual = gtfs_retrieve_FS.obj

        self.assertEqual(expected, actual)

    def test_get_file_metadata(self):
        gtfs_retrieve_FS.add_file_metadata('foo', 'bar', 36003600, 'foobar')
        actual = gtfs_retrieve_FS.get_file_metadata('foobar')

        expected = {'local_filename': 'bar', 'remote_filename': 'foo', 'timestamp_datetime': 36003600}

        self.assertEqual(expected, actual)

    def test_get_latest_local_timestamp(self):
        gtfs_retrieve_FS.add_file_metadata('foo1', 'bar1', 36003600, 'foobar')
        gtfs_retrieve_FS.add_file_metadata('foo1', 'bar2', 99999999, 'foobar')

        actual = gtfs_retrieve_FS.get_latest_local_timestamp('foo1')
        expected = 99999999

        self.assertEqual(expected, actual)

    def test_get_latest_local_timestamp_not_exist_file(self):
        gtfs_retrieve_FS.add_file_metadata('foo1', 'bar1', 36003600, 'foobar')
        gtfs_retrieve_FS.add_file_metadata('foo1', 'bar2', 99999999, 'foobar')

        actual = gtfs_retrieve_FS.get_latest_local_timestamp('foo22')
        expected = gtfs_retrieve_FS.MIN_EPOCH_TIME

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

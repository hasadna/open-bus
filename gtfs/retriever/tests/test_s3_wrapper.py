import unittest
import s3_wrapper
import datetime
from dateutil.tz import tzutc
from types import MappingProxyType


class TestFoo(unittest.TestCase):
    def test_cli_with_upload_command(self):
        # Prepare
        arguments = "s3_wrapper.py upload -aki aaa -sak bbb -lf ccc -k ddd -bn bucket42".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(aws_access_key_id='aaa',
                        command='upload',
                        cloud_key='ddd',
                        local_file='ccc',
                        aws_secret_access_key='bbb',
                        bucket_name='bucket42',
                        is_folder=False,
                        path_filter=None,
                        endpoint_url=None,
                        access_preset= None)
        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_download_command(self):
        # Prepare
        arguments = "s3_wrapper.py download -aki aaa -sak bbb -lf ccc -k ddd -bn bucket42".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(aws_access_key_id='aaa',
                        command='download',
                        cloud_key='ddd',
                        local_file='ccc',
                        aws_secret_access_key='bbb',
                        bucket_name='bucket42',
                        endpoint_url=  None,
                        access_preset=None)
        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_upload_command_with_default_bucket_name(self):
        # Prepare
        arguments = "s3_wrapper.py upload -aki aaa -sak bbb -lf ccc -k ddd".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(aws_access_key_id='aaa',
                        command='upload',
                        cloud_key='ddd',
                        local_file='ccc',
                        aws_secret_access_key='bbb',
                        bucket_name=None,
                        is_folder=False,
                        path_filter=None,
                        endpoint_url=None,
                        access_preset=None)
        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_upload_command_with_folder_mode(self):
        # Prepare
        arguments = "s3_wrapper.py upload -aki aaa -sak bbb -lf ccc -k ddd -fd".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(aws_access_key_id='aaa',
                        command='upload',
                        cloud_key='ddd',
                        local_file='ccc',
                        aws_secret_access_key='bbb',
                        bucket_name=None,
                        is_folder=True,
                        path_filter=None,
                        endpoint_url=None,
                        access_preset=None)

        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_download_command_with_default_bucket_name(self):
        # Prepare
        arguments = "s3_wrapper.py download -aki aaa -sak bbb -lf ccc -k ddd".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(aws_access_key_id='aaa',
                        command='download',
                        cloud_key='ddd',
                        local_file='ccc',
                        aws_secret_access_key='bbb',
                        bucket_name=None,
                        endpoint_url=None,
                        access_preset=None)
        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_list_command(self):
        # Prepare
        arguments = "s3_wrapper.py list -aki aaa -sak bbb -pf pre -rf reg".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(aws_access_key_id='aaa',
                        command='list',
                        aws_secret_access_key='bbb',
                        bucket_name=None,
                        prefix_filter='pre',
                        regex_filter='reg',
                        endpoint_url=None,
                        access_preset=None)
        # Test
        self.assertEqual(expected, actual)

    def test_regex_filter(self):
        # Prepare
        items = [{'Key': 'tmp/ob.jpg',
                  'LastModified': datetime.datetime(2018, 9, 1, 15, 30, 15, 983000, tzinfo=tzutc()),
                  'ETag': '"4c27e684add7202da1f99db6712a425b"',
                  'Size': 1381893,
                  'StorageClass': 'STANDARD',
                  'Owner': {'DisplayName': '1629867', 'ID': '1629867'}},
                 {'Key': 'tmp/image_of_a_bus2.jpg',
                  'LastModified': datetime.datetime(2018, 9, 1, 15, 30, 15, 983000, tzinfo=tzutc()),
                  'ETag': '"4c27e684add7202da1f99db6712a425b"',
                  'Size': 1381893,
                  'StorageClass': 'STANDARD',
                  'Owner': {'DisplayName': '1629867', 'ID': '1629867'}}
                 ]
        regex_argument = '.*ob.*'
        # Execute
        actual = s3_wrapper._regex_filter(items, regex_argument)
        # Expected
        expected = [{'Key': 'tmp/ob.jpg',
                     'LastModified': datetime.datetime(2018, 9, 1, 15, 30, 15, 983000, tzinfo=tzutc()),
                     'ETag': '"4c27e684add7202da1f99db6712a425b"',
                     'Size': 1381893,
                     'StorageClass': 'STANDARD',
                     'Owner': {'DisplayName': '1629867', 'ID': '1629867'}}]
        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_list_command_regex_all(self):
        # Prepare
        items = [{'Key': 'tmp/ob.jpg',
                  'LastModified': datetime.datetime(2018, 9, 1, 15, 30, 15, 983000, tzinfo=tzutc()),
                  'ETag': '"4c27e684add7202da1f99db6712a425b"',
                  'Size': 1381893,
                  'StorageClass': 'STANDARD',
                  'Owner': {'DisplayName': '1629867', 'ID': '1629867'}},
                 {'Key': 'tmp/image_of_a_bus2.jpg',
                  'LastModified': datetime.datetime(2018, 9, 1, 15, 30, 15, 983000, tzinfo=tzutc()),
                  'ETag': '"4c27e684add7202da1f99db6712a425b"',
                  'Size': 1381893,
                  'StorageClass': 'STANDARD',
                  'Owner': {'DisplayName': '1629867', 'ID': '1629867'}}
                 ]
        regex_argument = '.*'
        # Execute
        actual = s3_wrapper._regex_filter(items, regex_argument)
        # Expected
        expected = items
        # Test
        self.assertEqual(expected, actual)

    def test_list_content(self):

        actual = s3_wrapper.list_content(Mock())

        self.assertEqual(expected_list, actual)

    def test_list_content_with_regex(self):

        actual = s3_wrapper.list_content(Mock(), regex_argument='[b].*')

        self.assertEqual(expected_list, actual)

    def test_is_exist(self):
        actual = s3_wrapper.is_exist(Mock(), "foo")
        self.assertEqual(True, actual)

    def test_create_items_from_local_folder_is_folder_False(self):
        # prepare
        file_path = 'foo'
        key_name = 'bar'
        # Execute
        actual = s3_wrapper._create_items_from_local_folder(False, file_path, key_name)
        # Expected
        expected = [(file_path, key_name)]
        # Test
        self.assertEqual(expected, actual)

    def test_create_items_from_local_folder_is_folder_True_NonExistPath(self):
        with self.assertRaises(FileNotFoundError):
            s3_wrapper._create_items_from_local_folder(True, 'NonExistPath', '')

    def test_create_items_from_local_folder_is_folder_True_given_path_is_not_folder(self):
        file_path = 'tests/resources/test_folder_hierarchy/foo.txt'

        with self.assertRaises(NotADirectoryError):
            s3_wrapper._create_items_from_local_folder(True, file_path, 'foo')

    def test_create_items_from_local_folder_is_folder_True(self):
        file_path = 'tests/resources/test_folder_hierarchy'
        key_prefix = 'dfgdfgdfg'
        actual = s3_wrapper._create_items_from_local_folder(True, file_path, key_prefix)
        print(actual)
        expected = [(file_path+'/bar.txt', key_prefix + '/bar.txt'),
                    (file_path+'/foo.txt', key_prefix + '/foo.txt')]
        self.assertEqual(expected, actual)

    def test_create_items_from_local_folder_is_folder_True_with_filtert1(self):
        file_path = 'tests/resources/test_folder_hierarchy'
        key_prefix = 'dfgdfgdfg'
        actual = s3_wrapper._create_items_from_local_folder(True, file_path, key_prefix, "*.txt")
        print(actual)
        expected = [(file_path+'/bar.txt', key_prefix + '/bar.txt'),
                    (file_path+'/foo.txt', key_prefix + '/foo.txt')]
        self.assertEqual(expected, actual)

    def test_create_items_from_local_folder_is_folder_True_with_filtert2(self):
        file_path = 'tests/resources/test_folder_hierarchy'
        key_prefix = 'dfgdfgdfg'
        actual = s3_wrapper._create_items_from_local_folder(True, file_path, key_prefix, "bar*")
        print(actual)
        expected = [(file_path+'/bar.txt', key_prefix + '/bar.txt')]
        self.assertEqual(expected, actual)

    def test_make_crud_args_use_default_values(self):
        cli_arguments = ("s3_wrapper.py download -aki aaa -sak bbb -lf ccc -k ddd --access-preset " +
                         s3_wrapper._DIGITALOCEAN_PRIVATE).split()
        # Execute
        parsed_args = s3_wrapper.parse_cli_arguments(cli_arguments[1:])
        defr = MappingProxyType({s3_wrapper._DIGITALOCEAN_PRIVATE: {'bucket_name': '_DIGITALOCEAN_bucket_name',
                                                            'endpoint_url': '_DIGITALOCEAN_endpoint_url'}})

        actual = s3_wrapper.make_crud_args(parsed_args, defr)
        expected = {'aws_access_key_id': 'aaa',
                    'bucket_name': '_DIGITALOCEAN_bucket_name',
                    'endpoint_url': '_DIGITALOCEAN_endpoint_url',
                    'aws_secret_access_key': 'bbb'}

        self.assertEqual(expected, actual)

    def test_make_crud_args_without_default_values(self):
        cli_arguments = "s3_wrapper.py download -aki aaa -sak bbb -lf ccc -k ddd -bn mybucket".split()
        # Execute
        parsed_args = s3_wrapper.parse_cli_arguments(cli_arguments[1:])

        actual = s3_wrapper.make_crud_args(parsed_args)
        expected = {'aws_access_key_id': 'aaa',
                    'bucket_name': 'mybucket',
                    'aws_secret_access_key': 'bbb'}

        self.assertEqual(expected, actual)

    def test_download(self):

        local_key = 'local_key'
        remote_key = 'remote_key'

        s3_crud_mock = Mock()
        # Execute
        s3_wrapper.download(s3_crud_mock, local_key,remote_key)
        self.assertEqual(local_key, s3_crud_mock.local_file)
        self.assertEqual(remote_key, s3_crud_mock.cloud_key)

    def test_upload(self):

        local_key = 'local_key'
        remote_key = 'remote_key'

        s3_crud_mock = Mock()
        # Execute
        s3_wrapper.upload(s3_crud_mock, local_key,remote_key,False,None)
        self.assertEqual(local_key, s3_crud_mock.local_file)
        self.assertEqual(remote_key, s3_crud_mock.cloud_key)


    def test_upload_bytes(self):

        # Execute

        self.assertEqual('500.0bytes', s3_wrapper._sizeof_fmt(500))
        self.assertEqual('14.6KB', s3_wrapper._sizeof_fmt(15000))
        self.assertEqual('1.4MB', s3_wrapper._sizeof_fmt(1500000))
        self.assertEqual('1.4GB', s3_wrapper._sizeof_fmt(1500000000))




expected_list = [{'Key': 'tmp/ob.jpg',
                  'LastModified': datetime.datetime(2018, 9, 1, 15, 30, 15, 983000, tzinfo=tzutc()),
                  'ETag': '"4c27e684add7202da1f99db6712a425b"',
                  'Size': 1381893,
                  'StorageClass': 'STANDARD',
                  'Owner': {'DisplayName': '1629867', 'ID': '1629867'}},
                 {'Key': 'tmp/image_of_a_bus2.jpg',
                  'LastModified': datetime.datetime(2018, 9, 1, 15, 30, 15, 983000, tzinfo=tzutc()),
                  'ETag': '"4c27e684add7202da1f99db6712a425b"',
                  'Size': 1381893,
                  'StorageClass': 'STANDARD',
                  'Owner': {'DisplayName': '1629867', 'ID': '1629867'}}
                 ]


class Mock(s3_wrapper.S3Crud):

    def __init__(self):
        super().__init__(**{'bucket_name':'b_name'})

    def list_bucket_files(self, prefix_filter=''):
        return expected_list

    def is_key_exist(self, key_name):
        return True

    def download_one_file(self, local_file: str, cloud_key: str):
        self.local_file = local_file
        self.cloud_key = cloud_key
    def upload_one_file(self, local_file: str, cloud_key: str):
        self.local_file = local_file
        self.cloud_key = cloud_key

if __name__ == '__main__':
    unittest.main()

import unittest
import s3_wrapper
from types import MappingProxyType


class TestFoo(unittest.TestCase):
    def test_cli_with_upload_command(self):
        # Prepare
        arguments = "s3_wrapper.py upload -aki aaa -sak bbb -lf ccc -k ddd -bn bucket42".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(access_key_id='aaa',
                        command='upload',
                        cloud_key='ddd',
                        local_file='ccc',
                        secret_access_key='bbb',
                        bucket_name='bucket42',
                        is_folder=False,
                        path_filter=None,
                        aws=False)
        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_download_command(self):
        # Prepare
        arguments = "s3_wrapper.py download -aki aaa -sak bbb -lf ccc -k ddd -bn bucket42".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(access_key_id='aaa',
                        command='download',
                        cloud_key='ddd',
                        local_file='ccc',
                        secret_access_key='bbb',
                        bucket_name='bucket42',
                        aws=False)
        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_upload_command_with_default_bucket_name(self):
        # Prepare
        arguments = "s3_wrapper.py upload -aki aaa -sak bbb -lf ccc -k ddd".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(access_key_id='aaa',
                        command='upload',
                        cloud_key='ddd',
                        local_file='ccc',
                        secret_access_key='bbb',
                        bucket_name=None,
                        is_folder=False,
                        path_filter=None,
                        aws=False)
        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_upload_command_with_folder_mode(self):
        # Prepare
        arguments = "s3_wrapper.py upload -aki aaa -sak bbb -lf ccc -k ddd -fd".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(access_key_id='aaa',
                        command='upload',
                        cloud_key='ddd',
                        local_file='ccc',
                        secret_access_key='bbb',
                        bucket_name=None,
                        is_folder=True,
                        path_filter=None,
                        aws=False)

        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_download_command_with_default_bucket_name(self):
        # Prepare
        arguments = "s3_wrapper.py download -aki aaa -sak bbb -lf ccc -k ddd".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(access_key_id='aaa',
                        command='download',
                        cloud_key='ddd',
                        local_file='ccc',
                        secret_access_key='bbb',
                        bucket_name=None,
                        aws=False)
        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_list_command(self):
        # Prepare
        arguments = "s3_wrapper.py list -aki aaa -sak bbb -pf pre -rf reg".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(access_key_id='aaa',
                        command='list',
                        secret_access_key='bbb',
                        bucket_name=None,
                        prefix_filter='pre',
                        regex_filter='reg',
                        aws=False)
        # Test
        self.assertEqual(expected, actual)

    def test_regex_filter(self):
        # Prepare
        strings = ['foo', 'bar', 'foobar']
        regex_argument = '.*ob.*'
        # Execute
        actual = s3_wrapper._regex_filter(strings, regex_argument)
        # Expected
        expected = ['foobar']
        # Test
        self.assertEqual(expected, actual)

    def test_cli_with_list_command_regex_all(self):
        # Prepare
        strings = ['foo', 'bar', 'foobar']
        regex_argument = '.*'
        # Execute
        actual = s3_wrapper._regex_filter(strings, regex_argument)
        # Expected
        expected = strings
        # Test
        self.assertEqual(expected, actual)

    def test_list_content(self):

        actual = s3_wrapper.list_content(Mock())

        self.assertEqual(expected_list, actual)

    def test_list_content_with_regex(self):

        actual = s3_wrapper.list_content(Mock(), regex_argument='[b].*')

        self.assertEqual(['bar'], actual)

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
        file_path = 'resources/test_folder_hierarchy/foo.txt'

        with self.assertRaises(NotADirectoryError):
            s3_wrapper._create_items_from_local_folder(True, file_path, 'foo')

    def test_create_items_from_local_folder_is_folder_True(self):
        file_path = 'resources/test_folder_hierarchy'
        key_prefix = 'dfgdfgdfg'
        actual = s3_wrapper._create_items_from_local_folder(True, file_path, key_prefix)
        print(actual)
        expected = [(file_path+'/bar.txt', key_prefix + '/bar.txt'),
                    (file_path+'/foo.txt', key_prefix + '/foo.txt')]
        self.assertEqual(expected, actual)

    def test_create_items_from_local_folder_is_folder_True_with_filtert1(self):
        file_path = 'resources/test_folder_hierarchy'
        key_prefix = 'dfgdfgdfg'
        actual = s3_wrapper._create_items_from_local_folder(True, file_path, key_prefix, "*.txt")
        print(actual)
        expected = [(file_path+'/bar.txt', key_prefix + '/bar.txt'),
                    (file_path+'/foo.txt', key_prefix + '/foo.txt')]
        self.assertEqual(expected, actual)

    def test_create_items_from_local_folder_is_folder_True_with_filtert2(self):
        file_path = 'resources/test_folder_hierarchy'
        key_prefix = 'dfgdfgdfg'
        actual = s3_wrapper._create_items_from_local_folder(True, file_path, key_prefix, "bar*")
        print(actual)
        expected = [(file_path+'/bar.txt', key_prefix + '/bar.txt')]
        self.assertEqual(expected, actual)

    def test_make_crud_args_use_default_values(self):
        cli_arguments = "s3_wrapper.py download -aki aaa -sak bbb -lf ccc -k ddd".split()
        # Execute
        parsed_args = s3_wrapper.parse_cli_arguments(cli_arguments[1:])
        defr = MappingProxyType({s3_wrapper._DIGITALOCEAN: {'bucket_name': '_DIGITALOCEAN_bucket_name',
                                                            'endpoint_url': '_DIGITALOCEAN_endpoint_url'}})

        actual = s3_wrapper.make_crud_args(parsed_args, defr)
        expected = {'access_key_id': 'aaa',
                    'bucket_name': '_DIGITALOCEAN_bucket_name',
                    'endpoint_url': '_DIGITALOCEAN_endpoint_url',
                    'secret_access_key': 'bbb'}

        self.assertEqual(expected, actual)

    def test_make_crud_args_without_default_values(self):
        cli_arguments = "s3_wrapper.py download -aki aaa -sak bbb -lf ccc -k ddd -bn mybucket".split()
        # Execute
        parsed_args = s3_wrapper.parse_cli_arguments(cli_arguments[1:])

        actual = s3_wrapper.make_crud_args(parsed_args)
        expected = {'access_key_id': 'aaa',
                    'bucket_name': 'mybucket',
                    'secret_access_key': 'bbb'}

        self.assertEqual(expected, actual)


expected_list = ['foo', 'bar']


class Mock(s3_wrapper.S3Crud):

    def __init__(self):
        super().__init__('', '', '')

    def list_bucket_files(self, prefix_filter=''):
        return expected_list

    def is_key_exist(self, key_name):
        return True


if __name__ == '__main__':
    unittest.main()
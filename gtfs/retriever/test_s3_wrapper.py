import s3_wrapper
from unittest import TestCase


class TestFoo(TestCase):
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
                        bucket_name='bucket42')
        # Test
        self.assertEqual(actual, expected)

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
                        bucket_name='bucket42')
        # Test
        self.assertEqual(actual, expected)

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
                        bucket_name='obus-do1')
        # Test
        self.assertEqual(actual, expected)

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
                        bucket_name='obus-do1')
        # Test
        self.assertEqual(actual, expected)

    def test_cli_with_list_command(self):
        # Prepare
        arguments = "s3_wrapper.py list -aki aaa -sak bbb -pf pre -rf reg".split()
        # Execute
        actual = s3_wrapper.parse_cli_arguments(arguments[1:]).__dict__
        # Expected
        expected = dict(access_key_id='aaa',
                        command='list',
                        secret_access_key='bbb',
                        bucket_name='obus-do1',
                        prefix_filter='pre',
                        regex_filter='reg')
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


expected_list = ['foo', 'bar']


class Mock(s3_wrapper.S3Crud):

    def __init__(self):
        super().__init__('', '', '')

    def list_bucket_files(self, prefix_filter=''):
        return expected_list

    def is_key_exist(self, key_name):
        return True

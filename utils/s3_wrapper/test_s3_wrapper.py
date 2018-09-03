import s3_wrapper
from unittest import TestCase


class TestFoo(TestCase):
    def test_cli_with_upload_command(self):
        # Prepare
        arguments = "s3_wrapper.py upload -aki aaa -sak bbb -lf ccc -k ddd -bn bucket42".split()
        # Execute
        actual = s3_wrapper.cli(arguments[1:]).__dict__
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
        actual = s3_wrapper.cli(arguments[1:]).__dict__
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
        actual = s3_wrapper.cli(arguments[1:]).__dict__
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
        actual = s3_wrapper.cli(arguments[1:]).__dict__
        # Expected
        expected = dict(access_key_id='aaa',
                        command='download',
                        cloud_key='ddd',
                        local_file='ccc',
                        secret_access_key='bbb',
                        bucket_name='obus-do1')
        # Test
        self.assertEqual(actual, expected)

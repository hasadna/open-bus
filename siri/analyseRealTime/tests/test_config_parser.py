import unittest

import ConfigFileParser


class MyTestCase(unittest.TestCase):
    def test_get_args_from_cli(self):
        actual = ConfigFileParser.get_args_from_cli("blablabla -c configurations.config -d 20170202".split())
        self.assertEqual( actual.date_for_query, '20170202')
        self.assertEqual(actual.config_file, 'configurations.config')

    def test_parse_config(self):

        res = ConfigFileParser._parse_config('resources/test.config')

        self.assertEqual(res.connection_type,'connection_type')
        self.assertEqual(res.database_pass,'database_pass')
        self.assertEqual(res.database_user,'database_user')
        self.assertEqual(res.database_name,'database_name')
        self.assertEqual(res.bind_port,'8080')
        self.assertEqual(res.bind_address,'127.0.0.1')
        self.assertEqual(res.ssh_username,'ssh_username')
        self.assertEqual(res.remote_server,'192.168.10.50')
        self.assertEqual(res.write_results_to_file,False)

    def test_get_connection_parameters(self):

        # execute
        actual = ConfigFileParser.get_connection_parameters('resources/test.config')
        # test
        self.assertEqual(actual['connection_type'], 'connection_type')
        self.assertEqual(actual['database_pass'], 'database_pass')
        self.assertEqual(actual['database_user'], 'database_user')
        self.assertEqual(actual['database_name'], 'database_name')
        self.assertEqual(actual['bind_port'], 8080)
        self.assertEqual(actual['bind_address'], '127.0.0.1')
        self.assertEqual(actual['ssh_username'], 'ssh_username')
        self.assertEqual(actual['remote_server'], '192.168.10.50')
        self.assertEqual(actual['write_results_to_file'], False)

    def test_foo(self):

        excpected = {'connection':
                         {'remote_server': '192.168.10.50',
                          'ssh_username': 'ssh_username',
                          'bind_port': 8080,
                          'write_results_to_file': False,
                          'connection_type': 'connection_type',
                          'database_pass': 'database_pass',
                          'bind_address': '127.0.0.1',
                          'database_name': 'database_name',
                          'database_user': 'database_user'},
                     'date': '20170202'}

        actual = ConfigFileParser.wrapper("blablabla -c resources/test.config -d 20170202".split())

        self.assertEqual(actual,excpected)


if __name__ == '__main__':
    unittest.main()

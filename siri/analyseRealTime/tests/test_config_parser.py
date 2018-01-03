import unittest

import ConfigFileParser


class MyTestCase(unittest.TestCase):
    def test_get_args_from_cli(self):
        actual = ConfigFileParser.get_args_from_cli("blablabla -c configurations.config -d 20170202".split())
        self.assertEqual( actual.date_for_query, '20170202')
        self.assertEqual(actual.config_file, 'configurations.config')

    def test_parse_config(self):

        res = ConfigFileParser._parse_config('resources/conn.config')

        self.assertEqual(res.database_pass,'pass')
        self.assertEqual(res.database_user,'user')
        self.assertEqual(res.database_name,'name')
        self.assertEqual(res.database_port,'1234')
        #self.assertEqual(res.write_results_to_file,False)

    def test_get_connection_parameters(self):

        # execute
        actual = ConfigFileParser.get_connection_parameters('resources/conn.config')
        # test
#        self.assertEqual(actual['connection_type'], 'connection_type')
        self.assertEqual(actual['password'], 'pass')
        self.assertEqual(actual['user'], 'user')
        self.assertEqual(actual['database'], 'name')
        self.assertEqual(actual['port'], '1234')
        self.assertEqual(actual['host'], 'host')
        #self.assertEqual(actual['ssh_username'], 'ssh_username')
        #self.assertEqual(actual['remote_server'], '192.168.10.50')
        #self.assertEqual(actual['write_results_to_file'], False)

    def test_foo(self):

        excpected = {'connection': {'database': 'name', 'user': 'user', 'password': 'pass', 'host': 'host', 'port': '1234'}, 'date': '20170202'}

        actual = ConfigFileParser.wrapper("blablabla -c resources/conn.config -d 20170202".split())

        self.assertEqual(actual,excpected)


if __name__ == '__main__':
    unittest.main()

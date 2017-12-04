import unittest

import ConfigFileParser
import Cruds
import RealTimeArrivals

conn_config = ConfigFileParser.get_connection_parameters('../configurations.config')

class Connection(unittest.TestCase):
    def test_connection_establishment(self):
        # execute
        with Cruds.Connection(**conn_config) as c:
            # test
            with c.conn.cursor() as curs:
                curs.execute("select version();")
                self.assertTrue(curs.fetchone() is not None)

if __name__ == '__main__':
    unittest.main()

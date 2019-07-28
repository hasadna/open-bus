from datetime import datetime
from ..gtfs_utils.general_utils import parse_date


def test_parse_date():
    datetime_value, date_str = parse_date('gtfs/2019/04/17/2019-04-17T01-28-07_israel-public-transportation.zip')
    assert datetime_value == datetime(2019, 4, 17, 1, 28, 7)
    assert date_str == '2019-04-17'

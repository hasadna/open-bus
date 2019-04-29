import datetime
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../gtfs_utils/')
from general_utils import parse_date


def test_parse_date():
    date, date_str = parse_date('2099-01-01.zip')
    assert date == datetime.date(2099, 1, 1)
    assert date_str == '2099-01-01'

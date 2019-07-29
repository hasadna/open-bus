import datetime
import re

def parse_date(file_name):
    """
Parse date from file name
    :param file_name: file name
    :type file_name: str
    :return: datetime object and date string
    :rtype: tuple
    """

    match = re.match('.*/(\d+-\d+-\d+T\d+-\d+-\d+).*\.\w+', file_name)
    datetime_str = match.group(1)
    date_str = datetime_str.split('T')[0]
    datetime_value = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H-%M-%S')
    return datetime_value, date_str



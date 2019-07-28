import datetime
import re

def parse_date(file_name):
    """
Parse date from file name
    :param file_name: file name in YYYY-mm-dd.zip format
    :type file_name: str
    :return: date object and date string
    :rtype: tuple
    """

    match = re.match('.*/(\d+-\d+-\d+).*\.\w+', file_name)
    date_str = match.group(1)
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    return date, date_str



import datetime


def parse_date(file_name):
    """
Parse date from file name
    :param file_name: file name in YYYY-mm-dd.zip format
    :type file_name: str
    :return: date object and date string
    :rtype: tuple
    """
    date_str = file_name.split('.')[0]
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    return date, date_str



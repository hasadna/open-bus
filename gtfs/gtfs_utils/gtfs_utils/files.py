import datetime
import re
from os import listdir
from .configuration import configuration


def _get_existing_output_files(output_folder):
    """
Get existing output files in the given folder, in a list containing tuples of dates and output types.
    :param output_folder: a folder to check for
    :type output_folder:
    :return: list of 2-tuples (date_str, output_file_type)
    :rtype: list
    """
    return [(datetime.datetime.strptime(g[0], '%Y-%m-%d').date(), g[1]) for g in
            (re.match(configuration.files.output_file_name_regexp, file).groups()
             for file in listdir(output_folder))]


def get_dates_without_output(valid_dates, existing_output_files):
    """
    Get list of dates without output files (currently just route_stats is considered)
    :param valid_files: list of valid file keys
    :rtype: list of str
    :param existing_output_files: list of 2-tuples as returned by _get_existing_output_files
    :type existing_output_files: list
    :return: list of valid file keys for stat computation
    :rtype: list
    """
    return [date for date in valid_dates
            if date not in [g[0]
                            for g in existing_output_files
                            if g[1] == 'route_stats']]


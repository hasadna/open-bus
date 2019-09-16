import datetime
import re
from os import listdir
from os.path import split, join, exists
from typing import Tuple, List
from .configuration import configuration


def _get_existing_output_files(output_folder: str) -> List[Tuple[datetime.date, str]]:
    """
    Get existing output files in the given folder, in a list containing tuples of dates and output types.
    :param output_folder: a folder to check for
    :return: list of 2-tuples (date, output_file_type)
    """
    if not exists(output_folder):
        return []

    file_name_re = configuration.files.output_file_name_regexp
    file_type_re = configuration.files.output_file_type.replace('.', '\\.')
    regexp = file_name_re + '\\.' + file_type_re

    existing_output_files = []

    for file in listdir(output_folder):
        match = re.match(regexp, file)
        if match:
            date_str, stats_type = match.groups()
            file_type = (datetime.datetime.strptime(date_str, '%Y-%m-%d').date(), stats_type)
            existing_output_files.append(file_type)

    return existing_output_files


def get_dates_without_output(dates: List[datetime.date], output_folder: str) -> List[datetime.date]:
    """
    List dates without output files in the given folder (currently just route_stats is considered).
    :param dates: list of dates to check
    :param output_folder: a folder to check for
    :return: list of dates without output files
    """
    existing_output_files = _get_existing_output_files(output_folder)
    return [date
            for date
            in dates
            if date not in [g[0]
                            for g
                            in existing_output_files
                            if g[1] == 'route_stats']]


def remote_key_to_local_path(date: datetime.date, remote_key: str) -> str:
    local_file_name = split(remote_key)[-1]
    local_full_path = join(configuration.files.full_paths.gtfs_feeds,
                           date.strftime('%Y-%m-%d'),
                           local_file_name)
    return local_full_path

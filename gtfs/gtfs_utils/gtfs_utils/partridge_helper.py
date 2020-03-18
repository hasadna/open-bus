import datetime
import logging
from functools import lru_cache
from os.path import join, basename

import numpy as np
import partridge as ptg

from .configuration import load_configuration


def get_partridge_filter_for_date(zip_path: str, date: datetime.date):
    service_ids = ptg.read_service_ids_by_date(zip_path)[date]

    return {
        'trips.txt': {
            'service_id': service_ids,
        },
    }


def get_partridge_feed_by_date(zip_path: str, date: datetime.date):
    return ptg.feed(zip_path, view=get_partridge_filter_for_date(zip_path, date))


def write_filtered_feed_by_date(zip_path: str, date: datetime.date, output_path: str):
    ptg.writers.extract_feed(zip_path, output_path, get_partridge_filter_for_date(zip_path, date))


def prepare_partridge_feed(date: datetime.date,
                           gtfs_file_full_path: str,
                           filtered_feeds_directory=None):
    configuration = load_configuration()
    filtered_feeds_directory = filtered_feeds_directory or configuration.files.full_paths.filtered_feeds

    if configuration.write_filtered_feed:
        filtered_gtfs_path = join(filtered_feeds_directory, basename(gtfs_file_full_path))

        logging.info(f'Filtering gtfs feed for {date} from {gtfs_file_full_path} into {filtered_gtfs_path}')
        write_filtered_feed_by_date(gtfs_file_full_path, date, filtered_gtfs_path)

        logging.info(f'Reading filtered feed for file from path {filtered_gtfs_path}')
        feed = ptg.feed(filtered_gtfs_path)
    else:
        logging.info(f'Creating daily partridge feed for {date} from {gtfs_file_full_path}')
        feed = get_partridge_feed_by_date(gtfs_file_full_path, date)

    logging.debug(f'Finished creating daily partridge feed for {date} from {gtfs_file_full_path}')
    return feed


# Copied from partridge parsers, with a deletion of the seconds field
# it is used to to parse TripIdToDate since the departure time is in HH:MM format
# Why 2^17? See https://git.io/vxB2P.
@lru_cache(maxsize=2 ** 17)
def parse_time_no_seconds(val: str) -> np.float64:
    if val is np.nan:
        return val

    val = val.strip()

    if val == "":
        return np.nan

    h, m = val.split(":")
    ssm = int(h) * 3600 + int(m) * 60

    # pandas doesn't have a NaN int, use floats
    return np.float64(ssm)


parse_time_no_seconds_column = np.vectorize(parse_time_no_seconds)

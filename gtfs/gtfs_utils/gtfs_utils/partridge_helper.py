import datetime
import logging
import partridge as ptg
from os.path import join, basename
from .configuration import configuration


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
                           filtered_feeds_directory=configuration.files.full_paths.filtered_feeds):

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

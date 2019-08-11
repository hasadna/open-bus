# coding: utf-8
# Using a mix of `partridge` and `gtfstk` with some of my own additions to
# create daily statistical DataFrames for trips, routes and stops. 
# This will later become a module which we will run on our historical 
# MoT GTFS archive and schedule for nightly runs.

import pandas as pd
import datetime
import os
import logging
from os.path import join, split, dirname, basename
from typing import List, Dict
from zipfile import BadZipFile
from tqdm import tqdm
from partridge import feed as ptg_feed
from .files import _get_existing_output_files, get_dates_without_output
from .gtfs_utils import write_filtered_feed_by_date, get_partridge_feed_by_date, get_zones_df, \
    compute_route_stats, compute_trip_stats
from .environment import init_conf
from .s3 import get_latest_file, get_gtfs_file
from .logging_config import configure_logger
from .configuration import configuration
from .s3_wrapper import S3Crud
from .constants import GTFS_FILE_NAME, TARIFF_FILE_NAME


def get_closest_archive_path(date,
                             file_name,
                             archive_folder=configuration.files.full_paths.archive):
    for i in range(100):
        date_str = datetime.datetime.strftime(date - datetime.timedelta(i), '%Y-%m-%d')
        tariff_path_to_try = join(archive_folder, date_str, file_name)
        if os.path.exists(tariff_path_to_try):
            return tariff_path_to_try
    return join(configuration.files.baseDirectory, configuration.files.tariff_file_path)


def prepare_partridge_feed(date: datetime.date,
                           gtfs_file_full_path: str,
                           filtered_feeds_directory=configuration.files.full_paths.filtered_feeds):

    if configuration.write_filtered_feed:
        filtered_gtfs_path = join(filtered_feeds_directory, basename(gtfs_file_full_path))

        logging.info(f'Filtering gtfs feed for {date} from {gtfs_file_full_path} into {filtered_gtfs_path}')
        write_filtered_feed_by_date(gtfs_file_full_path, date, filtered_gtfs_path)

        logging.info(f'Reading filtered feed for file from path {filtered_gtfs_path}')
        feed = ptg_feed(filtered_gtfs_path)
    else:
        logging.info(f'Creating daily partridge feed for {date} from {gtfs_file_full_path}')
        feed = get_partridge_feed_by_date(gtfs_file_full_path, date)

    logging.debug(f'Finished creating daily partridge feed for {date} from {gtfs_file_full_path}')
    return feed


def log_trip_stats(ts: pd.DataFrame):
    # TODO: log more stats
    logging.debug(f'ts.shape={ts.shape}')
    logging.debug(f'dc_trip_id={ts.trip_id.nunique()}')
    logging.debug(f'dc_route_id={ts.route_id.nunique()}')
    logging.debug(f'num_start_zones={ts.start_zone.nunique()}')
    logging.debug(f'num_agency={ts.agency_name.nunique()}')


def log_route_stats(rs: pd.DataFrame):
    # TODO: log more stats
    logging.debug(f'rs.shape={rs.shape}')
    logging.debug(f'num_trips_sum={rs.num_trips.sum()}')
    logging.debug(f'dc_route_id={rs.route_id.nunique()}')
    logging.debug(f'num_start_zones={rs.start_zone.nunique()}')
    logging.debug(f'num_agency={rs.agency_name.nunique()}')


def save_trip_stats(ts: pd.DataFrame, output_path: str):
    logging.info(f'Saving trip stats result DF to gzipped pickle {output_path}')
    ts.to_pickle(output_path, compression='gzip')


def save_route_stats(rs: pd.DataFrame, output_path: str):
    logging.info(f'Saving route stats result DF to gzipped pickle {output_path}')
    rs.to_pickle(output_path, compression='gzip')


def handle_gtfs_date(date: datetime.date,
                     local_full_paths: Dict[str, str],
                     output_folder=configuration.files.full_paths.output,
                     archive_folder=configuration.files.full_paths.archive):
    """
Handle a single date for a single GTFS file. Download if necessary compute and save stats files (currently trip_stats
and route_stats).
    :param date_str: %Y-%m-%d
    :type date_str: str
    :param file: gtfs file name (currently only YYYY-mm-dd.zip)
    :type file: str
    :param bucket: s3 boto bucket object
    :type bucket: boto3.resources.factory.s3.Bucket
    :param output_folder: local path to write output files to
    :type output_folder: str
    :param gtfs_folder: local path containing GTFS feeds
    :type gtfs_folder: str
    """

    date_str = date.strftime('%Y-%m-%d')
    trip_stats_output_path = join(output_folder, date_str + '_trip_stats.pkl.gz')
    route_stats_output_path = join(output_folder, date_str + '_route_stats.pkl.gz')

    feed = prepare_partridge_feed(date, local_full_paths[GTFS_FILE_NAME])

    tariff_path_to_use = local_full_paths[TARIFF_FILE_NAME]
    logging.info(f'Creating zones DF from {tariff_path_to_use}')
    zones = get_zones_df(tariff_path_to_use)

    gtfs_file_base_name = basename(local_full_paths[GTFS_FILE_NAME])

    ts = compute_trip_stats(feed, zones, date, gtfs_file_base_name)
    save_trip_stats(ts, trip_stats_output_path)
    log_trip_stats(ts)

    rs = compute_route_stats(ts, date, gtfs_file_base_name)
    save_route_stats(rs, route_stats_output_path)
    log_route_stats(rs)


def get_dates_to_analyze(use_data_from_today: bool, date_range: List[str]) -> List[datetime.date]:
    if use_data_from_today:
        return [datetime.datetime.now().date()]
    else:
        if len(date_range) != 2:
            raise ValueError('date_range must be a 2-element list')

        min_date, max_date = [datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                              for date_str
                              in date_range]
        delta = max_date - min_date
        return [min_date + datetime.timedelta(days=days_delta)
                for days_delta
                in range(delta.days + 1)]


def remote_key_to_local_path(date: datetime.date, remote_key: str) -> str:
    local_file_name = split(remote_key)[-1]
    local_full_path = join(configuration.files.full_paths.gtfs_feeds,
                           date.strftime('%Y-%m-%d'),
                           local_file_name)
    return local_full_path


def batch_stats_s3(output_folder=configuration.files.full_paths.output,
                   gtfs_folder=configuration.files.full_paths.gtfs_feeds,
                   delete_downloaded_gtfs_zips=False):
    """
Create daily trip_stats and route_stats DataFrame pickles, based on the files in an S3 bucket and
their dates - `YYYY-mm-dd.zip`.
Will look for downloaded GTFS feeds with matching names in given gtfs_folder.
    :param bucket_name: name of s3 bucket with GTFS feeds
    :type bucket_name: str
    :param output_folder: local path to write output files to
    :type output_folder: str
    :param gtfs_folder: local path containing GTFS feeds
    :type gtfs_folder: str
    :param delete_downloaded_gtfs_zips: whether to delete GTFS feed files that have been downloaded by the function.
    :type delete_downloaded_gtfs_zips: bool
    """

    dates_to_analyze = get_dates_to_analyze(configuration.use_data_from_today,
                                            configuration.date_range)
    logging.debug(f'dates_to_analyze={dates_to_analyze}')

    try:
        os.makedirs(output_folder, exist_ok=True)
        dates_without_output = get_dates_without_output(dates_to_analyze, output_folder)

        crud = S3Crud.from_configuration(configuration.s3)
        logging.info(f'Connected to S3 bucket {configuration.s3.bucket_name}')

        file_types_to_download = [GTFS_FILE_NAME, TARIFF_FILE_NAME]
        remote_files_mapping = {}
        all_remote_files = []
        all_local_full_paths = []

        for desired_date in dates_without_output:
            for mot_file_name in file_types_to_download:
                if desired_date not in remote_files_mapping:
                    remote_files_mapping[desired_date] = {}

                date_and_key = get_latest_file(crud, mot_file_name, desired_date)
                remote_files_mapping[desired_date][mot_file_name] = date_and_key
                all_remote_files.append(date_and_key)

        logging.info(f'Starting files download, downloading {len(all_remote_files)} files')
        with tqdm(all_remote_files, unit='file', desc='Downloading') as progress_bar:
            for date, remote_file_key in progress_bar:
                progress_bar.set_postfix_str(remote_file_key)
                local_file_full_path = remote_key_to_local_path(date, remote_file_key)
                get_gtfs_file(remote_file_key, local_file_full_path, crud)
                all_local_full_paths.append(local_file_full_path)
        logging.info(f'Finished files download')

        logging.info(f'Starting analyzing files for {len(dates_without_output)} dates')
        with tqdm(dates_without_output, unit='date', desc='Analyzing') as progress_bar:
            for current_date in progress_bar:
                progress_bar.set_postfix_str(current_date)
                local_full_paths = {
                    mot_file_name: remote_key_to_local_path(current_date, remote_key)
                    for mot_file_name, (_, remote_key)
                    in remote_files_mapping[current_date].items()
                }
                handle_gtfs_date(current_date, local_full_paths, output_folder=output_folder)
        logging.info(f'Finished analyzing files')

        if delete_downloaded_gtfs_zips:
            logging.info(f'Starting removing downloaded files')
            with tqdm(all_local_full_paths, unit='file', desc='Removing') as progress_bar:
                for local_full_path in progress_bar:
                    os.remove(local_full_path)
                    if len(os.listdir(dirname(local_full_path))) == 0:
                        os.removedirs(dirname(local_full_path))
            logging.info(f'Finished removing downloaded files')
    except:
        logging.error('Failed', exc_info=True)


def main():
    init_conf()
    configure_logger()
    logging.info(f'starting batch_stats_s3 with default config')
    batch_stats_s3(delete_downloaded_gtfs_zips=configuration.delete_downloaded_gtfs_zip_files)


# TODO List
# 1. add a function for handling today's file only (download from ftp)
# 1. remove zone and extra route details from trip_stats
#   1. add them by merging to route_stats
# 1. separate to modules - run, conf, stats, utils...
# 1. logging - 
#   1. logging config and call in every function
#   1. BUG: logger not lsgging retries
#   1. log __name__ with decorator
#   1. add ids to every record - process, file
# 1. run older files with older tariff file
# 1. write tests
# 1. add time between stops - max, min, mean (using delta)

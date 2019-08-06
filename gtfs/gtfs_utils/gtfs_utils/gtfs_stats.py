# coding: utf-8
# Using a mix of `partridge` and `gtfstk` with some of my own additions to
# create daily statistical DataFrames for trips, routes and stops. 
# This will later become a module which we will run on our historical 
# MoT GTFS archive and schedule for nightly runs.

import pandas as pd
import datetime
import os
import re
import logging
from os.path import join, split
from typing import List
from zipfile import BadZipFile
from tqdm import tqdm
from partridge import feed as ptg_feed

from gtfs_utils.gtfs_utils.files import _get_existing_output_files, get_dates_without_output
from .gtfs_utils import write_filtered_feed_by_date, get_partridge_feed_by_date, get_zones_df, \
    compute_route_stats, compute_trip_stats
from .environment import init_conf
from .s3 import get_latest_file, get_gtfs_file
from .logging_config import configure_logger
from .configuration import configuration
from .s3_wrapper import S3Crud
from .constants import GTFS_FILE_NAME



def get_closest_archive_path(date,
                             file_name,
                             archive_folder=configuration.files.full_paths.archive):
    for i in range(100):
        date_str = datetime.datetime.strftime(date - datetime.timedelta(i), '%Y-%m-%d')
        tariff_path_to_try = join(archive_folder, date_str, file_name)
        if os.path.exists(tariff_path_to_try):
            return tariff_path_to_try
    return join(configuration.files.baseDirectory, configuration.files.tariff_file_path)


def handle_gtfs_date(date_str,
                     remote_file,
                     crud,
                     output_folder=configuration.files.full_paths.output,
                     gtfs_folder=configuration.files.full_paths.gtfs_feeds,
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
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    local_file_path = f'{date_str}.zip'
    local_file_full_path = join(gtfs_folder, local_file_path)

    downloaded = False

    trip_stats_output_path = join(output_folder, date_str + '_trip_stats.pkl.gz')
    if os.path.exists(trip_stats_output_path):
        logging.info(f'found trip stats result DF gzipped pickle "{trip_stats_output_path}"')
        ts = pd.read_pickle(trip_stats_output_path, compression='gzip')
    else:
        downloaded = get_gtfs_file(remote_file, local_file_full_path, crud)

        if configuration.write_filtered_feed:
            filtered_out_path = os.path.join(configuration.files.full_paths.filtered_feeds_directory,
                                             f'{date_str}.zip')
            logging.info(f'writing filtered gtfs feed for file "{local_file_full_path}" with date "{date}" in path '
                        f'{filtered_out_path}')
            write_filtered_feed_by_date(local_file_full_path, date, filtered_out_path)
            logging.info(f'reading filtered feed for file from path {filtered_out_path}')
            feed = ptg_feed(filtered_out_path)
        else:
            logging.info(f'creating daily partridge feed for file "{local_file_full_path}" with date "{date}"')
            try:
                feed = get_partridge_feed_by_date(local_file_full_path, date)
            except BadZipFile:
                logging.error('Bad local zip file', exc_info=True)
                downloaded = get_gtfs_file(remote_file, local_file_full_path, crud, force=True)
                feed = get_partridge_feed_by_date(local_file_full_path, date)

        logging.debug(f'finished creating daily partridge feed for file "{local_file_full_path}" with date "{date}"')

        # TODO: use Tariff.zip from s3
        tariff_path_to_use = get_closest_archive_path(date, 'Tariff.zip', archive_folder=archive_folder)
        logging.info(f'creating zones DF from "{tariff_path_to_use}"')
        zones = get_zones_df(tariff_path_to_use)

        logging.info(
            f'starting compute_trip_stats for file "{local_file_full_path}" with date "{date}" and zones '
            f'"{configuration.files.tariff_file_path}"')
        ts = compute_trip_stats(feed, zones, date_str, local_file_path)
        logging.debug(
            f'finished compute_trip_stats for file "{local_file_full_path}" with date "{date}" and zones '
            f'"{configuration.files.tariff_file_path}"')

        logging.info(f'saving trip stats result DF to gzipped pickle "{trip_stats_output_path}"')
        ts.to_pickle(trip_stats_output_path, compression='gzip')

    # TODO: log more stats
    logging.debug(
        f'ts.shape={ts.shape}, dc_trip_id={ts.trip_id.nunique()}, dc_route_id={ts.route_id.nunique()}, '
        f'num_start_zones={ts.start_zone.nunique()}, num_agency={ts.agency_name.nunique()}')

    logging.info(f'starting compute_route_stats from trip stats result')
    rs = compute_route_stats(ts, date_str, local_file_path)
    logging.debug(f'finished compute_route_stats from trip stats result')

    # TODO: log more stats
    logging.debug(
        f'rs.shape={rs.shape}, num_trips_sum={rs.num_trips.sum()}, dc_route_id={rs.route_id.nunique()}, '
        f'num_start_zones={rs.start_zone.nunique()}, num_agency={rs.agency_name.nunique()}')

    route_stats_output_path = join(output_folder, date_str + '_route_stats.pkl.gz')
    logging.info(f'saving route stats result DF to gzipped pickle "{route_stats_output_path}"')
    rs.to_pickle(route_stats_output_path, compression='gzip')

    return downloaded


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


def batch_stats_s3(bucket_name=configuration.s3.bucket_name,
                   output_folder=configuration.files.full_paths.output,
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
        existing_output_files = []
        if os.path.exists(output_folder):
            existing_output_files = _get_existing_output_files(output_folder)
            logging.info(f'found {len(existing_output_files)} output files in output folder {output_folder}')
        else:
            logging.info(f'creating output folder {output_folder}')
            os.makedirs(output_folder)

        dates_without_output = get_dates_without_output(dates_to_analyze, existing_output_files)

        crud = S3Crud(aws_access_key_id=configuration.s3.access_key_id,
                      aws_secret_access_key=configuration.s3.secret_access_key,
                      bucket_name=bucket_name,
                      endpoint_url=configuration.s3.s3_endpoint_url)
        logging.info(f'connected to S3 bucket {bucket_name}')

        files_mapping = {}
        all_files = []
        file_types_to_download = [GTFS_FILE_NAME]

        for desired_date in dates_without_output:
            for mot_file_name in file_types_to_download:
                if desired_date not in files_mapping:
                    files_mapping[desired_date] = {}

                date_and_key = get_latest_file(crud, mot_file_name, desired_date)
                files_mapping[desired_date][mot_file_name] = date_and_key
                all_files.append(date_and_key)


        logging.info(f'Starting files download, downloading {len(all_files)} files')
        with tqdm(all_files, unit='file', desc='Downloading') as progress_bar:
            for date, remote_file_key in progress_bar:
                local_file_name = split(remote_file_key)[-1]
                progress_bar.set_postfix_str(local_file_name)
                local_file_full_path = join(gtfs_folder, date.strftime('%Y-%m-%d'), local_file_name)
                get_gtfs_file(remote_file_key, local_file_full_path, crud)
        logging.info(f'Finished files download')

        logging.info(f'Starting analyzing files for {len(dates_without_output)} dates')
        with tqdm(dates_without_output, unit='date', desc='Analyzing') as progress_bar:
            for current_date in progress_bar:
                # TODO calc stuff for current_date with files in files_mapping[current_date]
                pass
        logging.info(f'Finished analyzing files')

        """
        with tqdm(dates_without_output, postfix='initializing', unit='file', desc='files') as t:
            for file in t:
                t.set_postfix_str(file)
                handle_gtfs_file(file,
                                 crud,
                                 output_folder=output_folder,
                                 gtfs_folder=gtfs_folder,
                                 delete_downloaded_gtfs_zips=delete_downloaded_gtfs_zips,
                                 stats_dates=file_dates_dict[file])

        logging.info(f'starting synchronous gtfs file download and stats computation from s3 bucket {bucket_name}')

        logging.info(f'finished synchronous gtfs file download and stats computation from s3 bucket {bucket_name}')
        """
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

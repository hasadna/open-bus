# coding: utf-8

# Using a mix of `partridge` and `gtfstk` with some of my own additions to 
# create daily statistical DataFrames for trips, routes and stops. 
# This will later become a module which we will run on our historical 
# MoT GTFS archive and schedule for nightly runs. 

import pandas as pd
import datetime
import os
import re
from os.path import join
import logging
from zipfile import BadZipFile
from tqdm import tqdm
from partridge import feed as ptg_feed
from .gtfs_utils import write_filtered_feed_by_date, get_partridge_feed_by_date, get_zones_df, \
    compute_route_stats, compute_trip_stats
from .environment import init_conf
from .s3 import get_valid_file_dates_dict, s3_download
from .logging_config import configure_logger
from .configuration import configuration
from .s3_wrapper import S3Crud


def _get_existing_output_files(output_folder):
    """
Get existing output files in the given folder, in a list containing tuples of dates and output types.
    :param output_folder: a folder to check for
    :type output_folder:
    :return: list of 2-tuples (date_str, output_file_type)
    :rtype: list
    """
    return [(g[0], g[1]) for g in
            (re.match(configuration.files.output_file_name_regexp, file).groups()
             for file in os.listdir(output_folder))]


def get_gtfs_file(remote_file: str,
                  local_file_full_path: str,
                  crud: S3Crud,
                  force: bool = False) -> bool:
    """
    :param remote_file: gtfs remote file key (as in S3)
    :param local_file_full_path: gtfs local file full path (typically /your/gtfs/dir/YYYY-mm-dd.zip)
    :param crud: S3Crud object
    :param force: force download or not
    :return: whether file was downloaded or not
    """

    if not force and os.path.exists(local_file_full_path):
        logging.info(f'Found local file "{local_file_full_path}"')
        return False

    logging.info(f'Starting file download with retries (key="{remote_file}", local path="{local_file_full_path}")')
    s3_download(crud, remote_file, local_file_full_path)
    logging.debug(f'Finished file download (key="{remote_file}", local path="{local_file_full_path}")')
    return True
    # TODO: log file size


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


def handle_gtfs_file(file,
                     crud,
                     stats_dates,
                     output_folder=configuration.files.full_paths.output,
                     gtfs_folder=configuration.files.full_paths.gtfs_feeds,
                     delete_downloaded_gtfs_zips=False):
    """
Handle a single GTFS file. Download if necessary compute and save stats files (currently trip_stats and route_stats).
    :param file: gtfs file name (currently only YYYY-mm-dd.zip)
    :type file: str
    :param bucket: s3 boto bucket object
    :type bucket: boto3.resources.factory.s3.Bucket
    :param output_folder: local path to write output files to
    :type output_folder: str
    :param gtfs_folder: local path containing GTFS feeds
    :type gtfs_folder: str
    :param delete_downloaded_gtfs_zips: whether to delete GTFS feed files that have been downloaded by the function.
    :type delete_downloaded_gtfs_zips: bool
    """

    downloaded = False
    with tqdm(stats_dates, postfix='initializing', unit='date', desc='dates', leave=False) as t:
        for date_str in t:
            t.set_postfix_str(date_str)
            downloaded = handle_gtfs_date(date_str, file, crud, output_folder=output_folder,
                                          gtfs_folder=gtfs_folder)

    if delete_downloaded_gtfs_zips and downloaded:
        logging.info(f'deleting gtfs zip file "{join(gtfs_folder, file)}"')
        os.remove(join(gtfs_folder, file))
    else:
        logging.debug(f'keeping gtfs zip file "{join(gtfs_folder, file)}"')


def batch_stats_s3(bucket_name=configuration.s3.bucket_name,
                   output_folder=configuration.files.full_paths.output,
                   gtfs_folder=configuration.files.full_paths.gtfs_feeds,
                   delete_downloaded_gtfs_zips=False,
                   forward_fill=configuration.forward_fill):
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
    :param forward_fill: flag for performing forward fill for missing dates using existing files
    :type forward_fill: bool
    """
    try:
        existing_output_files = []
        if os.path.exists(output_folder):
            existing_output_files = _get_existing_output_files(output_folder)
            logging.info(f'found {len(existing_output_files)} output files in output folder {output_folder}')
        else:
            logging.info(f'creating output folder {output_folder}')
            os.makedirs(output_folder)

        crud = S3Crud(aws_access_key_id=configuration.s3.access_key_id,
                      aws_secret_access_key=configuration.s3.secret_access_key
                      bucket_name=bucket_name,
                      endpoint_url=configuration.s3.s3_endpoint_url)

        logging.info(f'connected to S3 bucket {bucket_name}')

        file_dates_dict = get_valid_file_dates_dict(crud, existing_output_files, forward_fill)
        logging.debug(f'file_dates_dict={file_dates_dict}')


        non_empty_file_dates = {key: value for key, value in file_dates_dict.items() if len(file_dates_dict[key]) > 0}
        with tqdm(non_empty_file_dates, postfix='initializing', unit='file', desc='files') as t:
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
    except:
        logging.error('Failed', exc_info=True)


def main():
    init_conf()
    configure_logger()
    logging.info(f'starting batch_stats_s3 with default config')
    batch_stats_s3(delete_downloaded_gtfs_zips=configuration.delete_downloaded_gtfs_zip_files)


# ## What's next
# 
# TODO List
# 
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
# 1. add split_directions
# 1. add time between stops - max, min, mean (using delta)
# 1. add day and night headways and num_trips (maybe noon also)
# 1. mean_headway doesn't mean much when num_trips low (maybe num_trips cutoffs will be enough)

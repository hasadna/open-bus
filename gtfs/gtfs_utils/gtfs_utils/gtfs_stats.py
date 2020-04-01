# coding: utf-8
# Using a mix of `partridge` and `gtfstk` with some of my own additions to
# create daily statistical DataFrames for trips, routes and stops. 
# This will later become a module which we will run on our historical 
# MoT GTFS archive and schedule for nightly runs.

import datetime
import logging
import os
from os.path import join, dirname, basename, split
from typing import List, Dict, Set, Collection

import pandas as pd
from tqdm import tqdm

from .configuration import load_configuration, parse_conf_date_format
from .constants import GTFS_FILE_NAME, TARIFF_ZIP_NAME, CLUSTER_TO_LINE_ZIP_NAME, TRIP_ID_TO_DATE_ZIP_NAME
from .core_computations import get_zones_df, compute_route_stats, compute_trip_stats, get_clusters_df, \
    get_trip_id_to_date_df
from .environment import init_conf
from .local_files import get_dates_without_output, remote_key_to_local_path
from .logging_config import configure_logger
from .output import save_trip_stats, save_route_stats
from .partridge_helper import prepare_partridge_feed
from .s3 import get_latest_file, validate_download_size, fetch_remote_file, DateKeyTuple, MOTFileType
from .s3_wrapper import S3Crud

# A shorthand for {MOT file type: (found date, remote key)}
KeyMappingDict = Dict[MOTFileType, DateKeyTuple]


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


def analyze_gtfs_date(date: datetime.date,
                      local_full_paths: Dict[str, str],
                      output_folder: str = None,
                      output_file_type: str = None) -> List[str]:
    """
    Handles analysis of a single date for GTFS. Computes and saves stats files (currently trip_stats
    and route_stats).
    :param date: the analyzed date
    :param local_full_paths: a dict where keys are the required MOT file names, and values are full local paths
    :param output_folder: local path to write output files to
    :param output_file_type: The file type for the outputs (for example, csv.gz)
    """
    configuration = load_configuration()
    output_folder = output_folder or configuration.files.full_paths.output
    output_file_type = output_file_type or configuration.files.output_file_type

    date_str = date.strftime('%Y-%m-%d')
    trip_stats_output_path = join(output_folder, f'trip_stats_{date_str}.{output_file_type}')
    route_stats_output_path = join(output_folder, f'route_stats_{date_str}.{output_file_type}')

    feed = prepare_partridge_feed(date, local_full_paths[GTFS_FILE_NAME])

    tariff_file_path = local_full_paths[TARIFF_ZIP_NAME]
    logging.info(f'Creating zones DF from {tariff_file_path}')
    zones = get_zones_df(tariff_file_path)

    cluster_file_path = local_full_paths[CLUSTER_TO_LINE_ZIP_NAME]
    clusters = get_clusters_df(cluster_file_path)

    trip_id_to_date_path = local_full_paths[TRIP_ID_TO_DATE_ZIP_NAME]
    trip_id_to_date_df = get_trip_id_to_date_df(trip_id_to_date_path, date)

    source_files_base_name = []
    for file_name in sorted(local_full_paths.keys()):
        source_files_base_name += [basename(local_full_paths[file_name])]

    ts = compute_trip_stats(feed, zones, clusters, trip_id_to_date_df, date, source_files_base_name)
    save_trip_stats(ts, trip_stats_output_path)
    log_trip_stats(ts)

    rs = compute_route_stats(ts, date, source_files_base_name)
    save_route_stats(rs, route_stats_output_path)
    log_route_stats(rs)

    return [route_stats_output_path, trip_stats_output_path]


def get_dates_to_analyze(use_data_from_today: bool, date_range: List[str]) -> List[datetime.date]:
    if use_data_from_today:
        return [datetime.datetime.now().date()]
    elif len(date_range) == 1:
        return [parse_conf_date_format(date_range[0])]
    elif len(date_range) != 2:
            raise ValueError('Use "date_range" or set "use_data_from_today" to true if the configuration.')

    min_date, max_date = [parse_conf_date_format(date_str)
                          for date_str
                          in date_range]
    delta = max_date - min_date
    return [min_date + datetime.timedelta(days=days_delta)
            for days_delta
            in range(delta.days + 1)]


def batch_stats_s3(output_folder: str = None,
                   delete_downloaded_gtfs_zips: bool = False):
    """
    Create daily trip_stats and route_stats DataFrame pickles, based on the files in an S3 bucket
    and their dates.
    Will look for downloaded GTFS feeds with matching names in given gtfs_folder.
    :param output_folder: local path to write output files to
    :param delete_downloaded_gtfs_zips: Whether to delete GTFS feed files that have been downloaded by the function.
    """
    configuration = load_configuration()
    output_folder = output_folder or configuration.files.full_paths.output

    dates_to_analyze = get_dates_to_analyze(configuration.use_data_from_today,
                                            configuration.date_range)
    logging.debug(f'dates_to_analyze={dates_to_analyze}')

    try:
        os.makedirs(output_folder, exist_ok=True)
        if configuration.skip_date_with_output:
            dates_without_output = get_dates_without_output(dates_to_analyze, output_folder)
            logging.info(f"Skipped {len(dates_to_analyze) - len(dates_without_output)} dates "
                         f"that already had output files")
        else:
            dates_without_output = dates_to_analyze

        crud = S3Crud.from_configuration(configuration.s3)
        logging.info(f'Connected to S3 bucket {configuration.s3.bucket_name}')

        override_date = parse_conf_date_format(configuration.override_source_data_date)
        remote_files_mapping = get_dates_to_remote_keys_mapping(crud, dates_without_output,
                                                                override_gtfs_date=override_date)

        all_remote_files = generate_remote_keys_set_from_mapping(remote_files_mapping)
        all_local_full_paths = download_date_files(all_remote_files, crud,
                                                   force_existing_files=configuration.force_existing_files)

        logging.info(f'Starting analyzing files for {len(dates_without_output)} dates')
        all_result_files = []
        with tqdm(dates_without_output, unit='date', desc='Analyzing') as progress_bar:
            for current_date in progress_bar:
                progress_bar.set_postfix_str(current_date)
                local_full_paths = {
                    mot_file_name: remote_key_to_local_path(found_date, remote_key)
                    for mot_file_name, (found_date, remote_key)
                    in remote_files_mapping[current_date].items()
                }
                current_result_files = analyze_gtfs_date(current_date,
                                                         local_full_paths,
                                                         output_folder=output_folder)
                all_result_files.extend(current_result_files)
        logging.info(f'Finished analyzing files')

        if configuration.s3.upload_results:
            logging.info(f'Starting upload of {len(all_result_files)} result files')
            with tqdm(all_result_files, unit='file', desc='Uploading') as progress_bar:
                for current_file in progress_bar:
                    progress_bar.set_postfix_str(current_file)
                    cloud_results_path_prefix = configuration.s3.results_path_prefix.rstrip('/')
                    cloud_key = f'{cloud_results_path_prefix}/{split(current_file)[1]}'
                    logging.info(f'Uploading {current_file} to {cloud_key}')
                    crud.upload_one_file(current_file, cloud_key)
            logging.info(f'Finished upload of result files')

        if delete_downloaded_gtfs_zips:
            logging.info(f'Starting removal of downloaded files')
            with tqdm(all_local_full_paths, unit='file', desc='Removing') as progress_bar:
                for local_full_path in progress_bar:
                    os.remove(local_full_path)
                    if len(os.listdir(dirname(local_full_path))) == 0:
                        os.removedirs(dirname(local_full_path))
            logging.info(f'Finished removal of downloaded files')
    except:
        logging.error('Failed', exc_info=True)


def download_date_files(all_remote_files: Collection[DateKeyTuple], crud: S3Crud,
                        force_existing_files: bool = False) -> List[str]:
    """
    Download keys and return a list of the local paths
    :param all_remote_files: Iterable of (date, remote key) mapping
    :param crud: S3Crud
    :param force_existing_files: if true force downloading files that already exist
    :return:  A list of all the files local paths
    """
    all_local_full_paths = []
    files_size = validate_download_size([date_key[1] for date_key in all_remote_files], crud)
    logging.info(f'Starting files download, downloading {len(all_remote_files)} files, '
                 f'with total size {files_size/(1024**2)} MB')
    with tqdm(all_remote_files, unit='file', desc='Downloading') as progress_bar:
        for date, remote_file_key in progress_bar:
            progress_bar.set_postfix_str(remote_file_key)
            local_file_full_path = remote_key_to_local_path(date, remote_file_key)
            fetch_remote_file(remote_file_key, local_file_full_path, crud, force=force_existing_files)
            all_local_full_paths.append(local_file_full_path)
    logging.info(f'Finished files download')
    return all_local_full_paths


def generate_remote_keys_set_from_mapping(remote_keys_mapping: Dict[datetime.date, KeyMappingDict]) \
        -> Set[DateKeyTuple]:
    """
    Extract the tuples of the remote keys and dates from the mapping
    :param remote_keys_mapping: remote mapping generated by get_remote_keys_mapping_for_dates
    :return: a set of (found_date, remote_key)
    """
    tuples = set()
    for desired_date in remote_keys_mapping:
        for mot_file_type in remote_keys_mapping[desired_date]:
            tuples.add(remote_keys_mapping[desired_date][mot_file_type])
    return tuples


def get_dates_to_remote_keys_mapping(crud, dates_without_output: List[datetime.date],
                                     override_gtfs_date: datetime.date = None) \
        -> Dict[datetime.date, KeyMappingDict]:
    """
    For each date in the input, search for the newest MOT files
    :param crud: S3Crud
    :param dates_without_output: List of dates
    :param override_gtfs_date: If set overrides the desired date for files for all files
    :return: A dict like this: `{desired_date: {mot_file_name: (date_of_the_file, remote_key)}}`
    """
    if override_gtfs_date:
        override_date_keys = get_remote_keys_for_date(crud, override_gtfs_date)
        return {desired_date: override_date_keys for desired_date in dates_without_output}

    remote_files_mapping = {}
    for desired_date in dates_without_output:
        remote_keys = get_remote_keys_for_date(crud, desired_date)
        remote_files_mapping[desired_date] = remote_keys
    return remote_files_mapping


def get_remote_keys_for_date(crud: S3Crud, desired_date: datetime.date) -> KeyMappingDict:
    """
    returns a dict mapping an MOT file type to it's newest version before `desired_date`
    :param crud: S3Crudd object
    :param desired_date: The date to look for the file
    :return: a dict from MOT file type to (found_date, remote_key) tuple
    """
    file_types_to_download = [GTFS_FILE_NAME, TARIFF_ZIP_NAME, CLUSTER_TO_LINE_ZIP_NAME, TRIP_ID_TO_DATE_ZIP_NAME]
    remote_files_mapping = {}
    for mot_file_name in file_types_to_download:
        remote_files_mapping[mot_file_name] = get_latest_file(crud, mot_file_name, desired_date)
    return remote_files_mapping


def main():
    init_conf()
    configure_logger()
    logging.info(f'starting batch_stats_s3 with default config')
    configuration = load_configuration()
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

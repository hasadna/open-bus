import logging
import pandas as pd
import datetime
from collections import defaultdict
from tqdm import tqdm
from .s3_wrapper import list_content, S3Crud
from .retry import retry
from .general_utils import parse_date
from .configuration import configuration


@retry()
def s3_download(crud: S3Crud, key, output_path):
    """
Download file from s3 bucket. Retry using decorator.
    :param bucket: s3 boto bucket object
    :type bucket: boto3.resources.factory.s3.Bucket
    :param key: key of the file to download
    :type key: str
    :param output_path: output path to download the file to
    :type output_path: str
    """

    def hook(t):
        def inner(bytes_amount):
            t.update(bytes_amount)

        return inner

    if configuration.display_download_progress_bar:
        # TODO: this is an S3 anti-pattern, and is inefficient - so defaulting to not doing this
        if configuration.display_size_on_progress_bar:
            size = crud.get_file_size(key)
        else:
            size = None

        with tqdm(total=size, unit='B', unit_scale=True, desc='download ' + key, leave=True) as t:
            crud.download_one_file(output_path, key, callback=hook(t))
    else:
        crud.download_one_file(output_path, key)


def get_bucket_valid_files(crud):
    """
    Get list of valid files from bucket, as set by configuration.s3.bucket_valid_file_name_regexp
    :param bucket_objects: collection of bucket objects
    :type bucket_objects: s3.Bucket.objectsCollection
    :return: list of valid file keys
    :rtype: list of str
    """
    return [obj['Key']
            for obj
            in list_content(crud,
                            prefix_filter=configuration.s3.bucket_valid_file_name_regexp.pattern.split('\\')[0],
                            regex_argument=configuration.s3.bucket_valid_file_name_regexp)]


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


def get_forward_fill_dict(valid_files, future_days=configuration.future_days_count):
    """
    Get a dictionary mapping gtfs file names to a list of dates for forward fill by scanning for missing dates for files
    :param valid_files: list of valid file keys
    :rtype: list of str
    :return dictionary mapping file names to dates
    :rtype defaultdict of lists (defaults to empty list)
    """
    ffill = defaultdict(list)

    if not len(valid_files):
        return ffill

    date_to_file = {}
    date_str_to_file = {}

    for file in valid_files:
        current_file_datetime, current_file_date_str = parse_date(file)

        if current_file_date_str in date_str_to_file:
            # If there is already a file from this date
            other_datetime_in_same_date = next((existing_datetime
                                                for existing_datetime
                                                in date_to_file.keys()
                                                if existing_datetime.date() == current_file_datetime.date()))

            if other_datetime_in_same_date > current_file_datetime:
                # If the current file is newer than the already-existing one
                del date_to_file[other_datetime_in_same_date]
            else:
                # If the current file is older than the already-existing one
                continue

        date_to_file[current_file_datetime] = file
        date_str_to_file[current_file_date_str] = file

    existing_dates = pd.DatetimeIndex(date_to_file.keys())
    expected_dates = pd.DatetimeIndex(start=existing_dates.min(), end=existing_dates.max()+datetime.timedelta(days=future_days), freq='D')
    date_df = pd.Series(pd.NaT, expected_dates)
    date_df[existing_dates] = existing_dates
    date_df = date_df.fillna(method='ffill', limit=59)
    # TODO: remove dates that aren't in the 59 day gap
    # BUG: will act unexpectedly if more than 59 day gap
    for file_date, stats_date in zip(date_df.dt.strftime('%Y-%m-%d'), date_df.index.strftime('%Y-%m-%d')):
        ffill[date_str_to_file[file_date]].append(stats_date)

    return ffill


def get_valid_file_dates_dict(crud, existing_output_files):
    logging.info(f'configuration.s3.bucket_valid_file_name_regexp={configuration.s3.bucket_valid_file_name_regexp}')
    bucket_valid_files = get_bucket_valid_files(crud)
    logging.debug(f'bucket_valid_files: {bucket_valid_files}')

    logging.info(f'applying forward fill')
    ffill_dict = get_forward_fill_dict(bucket_valid_files)
    logging.info(f'found {sum([len(l) for l in ffill_dict.values()]) - len(bucket_valid_files)} missing dates for '
                'forward fill.')

    files_for_stats = defaultdict(list)
    for file in ffill_dict:
        files_for_stats[file] = get_dates_without_output(ffill_dict[file], existing_output_files)

    logging.info(f'found {len([key for key in files_for_stats if len(files_for_stats[key])>0])} GTFS files valid for '
                'stats calculations in bucket')
    logging.debug(f'Files: { {key: value for key, value in files_for_stats.items() if len(files_for_stats[key])>0} }')
    return files_for_stats

import logging
from typing import List, Tuple
import datetime
from collections import defaultdict
from tqdm import tqdm
from .s3_wrapper import list_content, S3Crud
from .retry import retry
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


def get_bucket_file_keys_for_date(crud: S3Crud,
                                  mot_file_name: str,
                                  date: datetime.datetime) -> List[str]:
    """
    Get list of files from bucket that fit the given MOT file name and are from the given date
    :return: list of file keys
    :rtype: list of str
    """
    prefix = datetime.datetime.strftime(date, 'gtfs/%Y/%m/%d/%Y-%m-%d')
    regexp = f'{prefix}.*{mot_file_name}'

    return [obj['Key'] for obj in list_content(crud, prefix_filter=prefix, regex_argument=regexp)]


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


def get_latest_file(crud: S3Crud,
                    mot_file_name: str,
                    desired_date: datetime.datetime,
                    past_days_to_try: int = 100) -> Tuple[datetime.date, str]:
    for i in range(past_days_to_try):
        date = desired_date - datetime.timedelta(i)
        bucket_files_in_date = get_bucket_file_keys_for_date(crud, mot_file_name, date)

        if len(bucket_files_in_date) > 0:
            bucket_files_in_date = sorted(bucket_files_in_date)
            date_and_key = (date, bucket_files_in_date[-1])
            return date_and_key


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

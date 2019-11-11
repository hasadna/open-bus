import logging
import datetime
import os.path
from os.path import dirname
from typing import List, Tuple
from tqdm import tqdm

from gtfs.gtfs_utils.gtfs_utils.environment import get_free_space_bytes
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
    :param crud: S3Crud object
    :param mot_file_name: Original name of the file from MOT
    :param date: Date to use as original file date when searching
    :return: list of file keys
    """
    prefix = datetime.datetime.strftime(date, 'gtfs/%Y/%m/%d/%Y-%m-%d')
    regexp = f'{prefix}.*{mot_file_name}'

    return [obj['Key'] for obj in list_content(crud, prefix_filter=prefix, regex_argument=regexp)]


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


def fetch_remote_file(remote_file_key: str,
                      local_file_full_path: str,
                      crud: S3Crud,
                      force: bool = False) -> bool:
    """
    :param remote_file_key: gtfs remote file key (in S3)
    :param local_file_full_path: gtfs local file full path
    :param crud: S3Crud object
    :param force: force download or not
    :return: whether file was downloaded or not
    """

    if not force and os.path.exists(local_file_full_path):
        logging.info(f'Found local file "{local_file_full_path}"')
        return False

    logging.info(f'Starting file download with retries (key="{remote_file_key}", local path="{local_file_full_path}")')
    s3_download(crud, remote_file_key, local_file_full_path)
    logging.debug(f'Finished file download (key="{remote_file_key}", local path="{local_file_full_path}")')
    return True
    # TODO: log file size


def is_enough_disk_space(remote_file_keys: List[str],
                         crud: S3Crud,
                         silent: True) -> bool:
    # confirm enough disk space
    local_dir = configuration.files.full_paths.gtfs_feeds
    free_space = get_free_space_bytes(local_dir)
    s3_files_size = sum([crud.get_file_size(file_name) for file_name in remote_file_keys])
    if not free_space > s3_files_size:
        if silent:
            return False
        raise IOError(
            f'There is no enough free disk space for {len(remote_file_keys)!r} files '
            f'to be saved in {local_dir!r}.\n'
            f'free space - {free_space / 1024 / 1024}MB '
            f'and the remotre files size is - {s3_files_size / 1024 / 1024}MB'
        )
    return True

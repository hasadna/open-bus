import logging
import pandas as pd
import datetime
from collections import defaultdict
from gtfs_stats_conf import BUCKET_VALID_FILES_RE
from retry import retry
from general_utils import parse_date
from configuration import configuration


@retry()
def s3_download(bucket, key, output_path):
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

    if configuration.displayDownloadProgressBar:
        # TODO: this is an S3 anti-pattern, and is inefficient - so defaulting to not doing this
        if configuration.displaySizeOnProgressBar:
            size = [obj.size for obj in bucket.objects.filter(Prefix=key, MaxKeys=1)][0]
        else:
            size = None

        with tqdm(total=size, unit='B', unit_scale=True, desc='download ' + key, leave=True) as t:
            bucket.download_file(key, output_path, Callback=hook(t))
    else:
        bucket.download_file(key, output_path)


def get_bucket_valid_files(bucket_objects):
    """
Get list of valid files from bucket, as set by BUCKET_VALID_FILES_RE
    :param bucket_objects: collection of bucket objects
    :type bucket_objects: s3.Bucket.objectsCollection
    :return: list of valid file keys
    :rtype: list of str
    """
    return [obj.key for obj in bucket_objects
            if re.match(BUCKET_VALID_FILES_RE, obj.key)]


def get_dates_without_output(valid_files, existing_output_files):
    """
Get list of dates without output files (currently just route_stats is considered)
    :param valid_files: list of valid file keys
    :rtype: list of str
    :param existing_output_files: list of 2-tuples as returned by _get_existing_output_files
    :type existing_output_files: list
    :return: list of valid file keys for stat computation
    :rtype: list
    """
    return [parse_date(file)[1] for file in valid_files
            if file not in [g[0] + '.zip'
                            for g in existing_output_files
                            if g[1] == 'route_stats']]


def get_forward_fill_dict(valid_files, future_days=configuration.futureDaysCount):
    """
get a dictionary mapping gtfs file names to a list of dates for forward fill by scanning for missing dates for files
    :param valid_files: list of valid file keys
    :rtype: list of str
    :return dictionary mapping file names to dates
    :rtype defaultdict of lists (defaults to empty list)
    """
    existing_dates = pd.DatetimeIndex([parse_date(file)[0] for file in valid_files])
    expected_dates = pd.DatetimeIndex(start=existing_dates.min(), end=existing_dates.max()+datetime.timedelta(days=future_days), freq='D')
    date_df = pd.Series(pd.NaT, expected_dates)
    date_df[existing_dates] = existing_dates
    date_df = date_df.fillna(method='ffill', limit=59)
    # TODO: remove dates that aren't in the 59 day gap
    # BUG: will act unexcpectedly if more than 59 day gap
    ffill = defaultdict(list)
    for file_date, stats_date in zip(date_df.dt.strftime('%Y-%m-%d'), date_df.index.strftime('%Y-%m-%d')):
        ffill[file_date + '.zip'].append(stats_date)

    return ffill


def get_valid_file_dates_dict(bucket_objects, existing_output_files, forward_fill):
    logging.info(f'BUCKET_VALID_FILES_RE={BUCKET_VALID_FILES_RE}')
    bucket_valid_files = get_bucket_valid_files(bucket_objects)
    if forward_fill:
        logging.info(f'applying forward fill')
        ffill_dict = get_forward_fill_dict(bucket_valid_files)
        logging.info(f'found {sum([len(l) for l in ffill_dict.values()]) - len(bucket_valid_files)} missing dates for '
                    'forward fill.')

        files_for_stats = defaultdict(list)
        for file in ffill_dict:
            files_for_stats[file] = get_dates_without_output([date_str + '.zip' for date_str in ffill_dict[file]],
                                                             existing_output_files)

    else:
        files_for_stats = defaultdict(list)
        for date in get_dates_without_output(bucket_valid_files, existing_output_files):
            files_for_stats[date + '.zip'].append(date)

    logging.info(f'found {len([key for key in files_for_stats if len(files_for_stats[key])>0])} GTFS files valid for '
                'stats calculations in bucket')
    logging.debug(f'Files: { {key: value for key, value in files_for_stats.items() if len(files_for_stats[key])>0} }')
    return files_for_stats

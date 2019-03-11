import re
import os.path

BASE_FOLDER = '..\\..\\..\\..\\'

DATA_FOLDER = os.path.join(BASE_FOLDER, 'data')

# LOCAL_TARIFF_PATH = DATA_FOLDER + 'archive/2019-03-07/Tariff.zip'
ARCHIVE_FOLDER = os.path.join(DATA_FOLDER, 'archive')
LOCAL_TARIFF_PATH = os.path.join(ARCHIVE_FOLDER, '2019-03-07', 'Tariff.zip')

GTFS_FEEDS_PATH = os.path.join(DATA_FOLDER, 'gtfs_feeds')

#OUTPUT_DIR = os.path.join(DATA_FOLDER, 'gtfs_stats_route_desc')
OUTPUT_DIR = os.path.join(DATA_FOLDER, 'gtfs_stats_hack')

OUTPUT_FILE_NAME_RE = re.compile('^(?P<date_str>[^_]+?)'
                                 '_(?P<type>\w+)\.pkl\.gz')

BUCKET_NAME = 's3.obus.hasadna.org.il'
# BUCKET_VALID_FILES_RE = re.compile('2019-0\d-\d\d\.zip')
BUCKET_VALID_FILES_RE = re.compile('2019-03-11.zip')

FORWARD_FILL = True
FUTURE_DAYS = 0  # will have an effect only if FORWARD_FILL is True

DOWNLOAD_PBAR = False
SIZE_FOR_DOWNLOAD_PBAR = False

DELETE_DOWNLOADED_GTFS_ZIPS = False
WRITE_FILTERED_FEED = False
FILTERED_FEEDS_PATH = os.path.join(DATA_FOLDER, 'filtered_feeds')

STATS_TYPES = ['trip_stats', 'route_stats']

LOG_FOLDER = os.path.join(BASE_FOLDER, 'logs')

PROFILE = False
PROFILE_PATH = os.path.join(BASE_FOLDER, 'gtfs_stats_180601.prof')

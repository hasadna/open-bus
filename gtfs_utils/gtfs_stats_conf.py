import re

BASE_FOLDER                = '../../'

DATA_FOLDER                = BASE_FOLDER + 'data/'

LOCAL_TARIFF_PATH          = DATA_FOLDER + 'sample/latest_tariff.zip' 
#LOCAL_TARIFF_PATH          = 'data/archive/2018-07-15/Tariff.zip'
GTFS_FEEDS_PATH            = DATA_FOLDER + 'gtfs_feeds/'

OUTPUT_DIR                 = DATA_FOLDER + 'gtfs_stats_MOD_zones_left/'

OUTPUT_FILE_NAME_RE        = re.compile('^(?P<date_str>[^_]+?)_(?P<type>\w+)\.pkl\.gz')

BUCKET_NAME                = 's3.obus.hasadna.org.il'
BUCKET_VALID_FILES_RE      = re.compile('2017-0\d-\d\d\.zip')
DELETE_DOWNLOADED_GTFS_ZIPS= False
WRITE_FEED_DANGEROUSLY     = False
FILTERED_FEEDS_PATH        = DATA_FOLDER + 'filtered_feeds/'

STATS_TYPES                = ['trip_stats', 'route_stats']

LOG_FOLDER                 = BASE_FOLDER + 'logs/'
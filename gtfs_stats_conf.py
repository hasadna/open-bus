import re

LOCAL_TARIFF_PATH = 'data/sample/latest_tariff.zip' 
#LOCAL_TARIFF_PATH = 'data/archive/2018-07-15/Tariff.zip'
GTFS_FEEDS_PATH = 'data/gtfs_feeds/'

OUTPUT_DIR = 'data/gtfs_stats_MOD_raw_feed/'

OUTPUT_FILE_NAME_RE = re.compile('^(?P<date_str>[^_]+?)_(?P<type>\w+)\.pkl\.gz')

BUCKET_NAME = 's3.obus.hasadna.org.il'
BUCKET_VALID_FILES_RE = re.compile('2017-0\d-\d\d\.zip')
DELETE_DOWNLOADED_GTFS_ZIPS = False
WRITE_FEED_DANGEROUSLY = True
FILTERED_FEEDS_PATH = 'data/filtered_feeds/'


STATS_TYPES = ['trip_stats', 'route_stats']

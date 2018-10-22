import re
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../gtfs_utils/')

from gtfs_stats_conf import \
    LOCAL_TARIFF_PATH, GTFS_FEEDS_PATH, OUTPUT_DIR, \
    OUTPUT_FILE_NAME_RE, BUCKET_NAME, BUCKET_VALID_FILES_RE, \
    DELETE_DOWNLOADED_GTFS_ZIPS, WRITE_FILTERED_FEED, \
    FILTERED_FEEDS_PATH, STATS_TYPES, LOG_FOLDER


def test_conf():
    assert isinstance(LOCAL_TARIFF_PATH, str)
    assert isinstance(GTFS_FEEDS_PATH, str)
    assert isinstance(OUTPUT_DIR, str)

    retype = type(re.compile('bus'))

    assert isinstance(OUTPUT_FILE_NAME_RE, retype)
    assert isinstance(BUCKET_NAME, str)
    assert isinstance(BUCKET_VALID_FILES_RE, retype)
    assert isinstance(DELETE_DOWNLOADED_GTFS_ZIPS, bool)
    assert isinstance(WRITE_FILTERED_FEED, bool)
    assert isinstance(FILTERED_FEEDS_PATH, str)
    assert isinstance(STATS_TYPES, list)
    assert isinstance(LOG_FOLDER, str)

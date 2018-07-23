import re

from gtfs_stats_conf import \
    LOCAL_TARIFF_PATH, GTFS_FEEDS_PATH, OUTPUT_DIR, \
    OUTPUT_FILE_NAME_RE, BUCKET_NAME, BUCKET_VALID_FILES_RE, \
    DELETE_DOWNLOADED_GTFS_ZIPS, WRITE_FEED_DANGEROUSLY, \
    FILTERED_FEEDS_PATH, STATS_TYPES


def test_conf():
    assert isinstance(LOCAL_TARIFF_PATH, str)
    assert isinstance(GTFS_FEEDS_PATH, str)
    assert isinstance(OUTPUT_DIR, str)

    retype = type(re.compile('bus'))

    assert isinstance(OUTPUT_FILE_NAME_RE, retype)
    assert isinstance(BUCKET_NAME, str)
    assert isinstance(BUCKET_VALID_FILES_RE, retype)
    assert isinstance(DELETE_DOWNLOADED_GTFS_ZIPS, bool)
    assert isinstance(WRITE_FEED_DANGEROUSLY, bool)
    assert isinstance(FILTERED_FEEDS_PATH, str)
    assert isinstance(STATS_TYPES, list)
    assert isinstance(LOG_FOLDER, str)

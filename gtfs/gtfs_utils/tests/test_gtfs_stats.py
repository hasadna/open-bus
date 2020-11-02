import datetime
import os
import filecmp
from os.path import dirname, join
from ..gtfs_utils.constants import GTFS_FILE_NAME, TARIFF_ZIP_NAME, CLUSTER_TO_LINE_ZIP_NAME, TRIP_ID_TO_DATE_ZIP_NAME
from ..gtfs_utils.gtfs_stats import analyze_gtfs_date


TEST_ASSETS_DIR = join(dirname(__file__), 'assets')
TEST_OUTPUTS_DIR = join(dirname(__file__), 'outputs')
TEST_FILE_DATE = datetime.datetime(2019, 3, 7).date()
TEST_FILE_DATE_STR = TEST_FILE_DATE.strftime('%Y-%m-%d')
INPUT_LOCAL_FULL_PATHS = {
    GTFS_FILE_NAME: join(TEST_ASSETS_DIR, 'inputs', '2019-03-07-israel-public-transportation.zip'),
    TARIFF_ZIP_NAME: join(TEST_ASSETS_DIR, 'inputs', '2019-03-07-Tariff.zip'),
    CLUSTER_TO_LINE_ZIP_NAME: join(TEST_ASSETS_DIR, 'inputs', '2019-03-07-ClusterToLine.zip'),
    TRIP_ID_TO_DATE_ZIP_NAME: join(TEST_ASSETS_DIR, 'inputs', '2019-03-07-TripIdToDate.zip'),
}
OUTPUT_FILE_TYPE = 'csv'
OUTPUT_FILE_NAMES = [
    f'trip_stats_{TEST_FILE_DATE_STR}.{OUTPUT_FILE_TYPE}',
    f'route_stats_{TEST_FILE_DATE_STR}.{OUTPUT_FILE_TYPE}',
]


def test_analyze_gtfs_date():
    os.makedirs(TEST_OUTPUTS_DIR, exist_ok=True)
    analyze_gtfs_date(date=TEST_FILE_DATE,
                      local_full_paths=INPUT_LOCAL_FULL_PATHS,
                      output_folder=TEST_OUTPUTS_DIR,
                      output_file_type=OUTPUT_FILE_TYPE)

    for file_name in OUTPUT_FILE_NAMES:
        expected_file = join(TEST_ASSETS_DIR, 'outputs', file_name)
        actual_file = join(TEST_OUTPUTS_DIR, file_name)

        assert filecmp.cmp(expected_file, actual_file)
        os.remove(actual_file)

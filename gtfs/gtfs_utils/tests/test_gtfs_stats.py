import datetime
import gzip
import os
import pickle
from os.path import dirname, join
from ..gtfs_utils.constants import GTFS_FILE_NAME, TARIFF_ZIP_NAME, CLUSTER_TO_LINE_ZIP_NAME
from ..gtfs_utils.gtfs_stats import analyze_gtfs_date


TEST_ASSETS_DIR = join(dirname(__file__), 'assets')
TEST_OUTPUTS_DIR = join(dirname(__file__), 'outputs')
TEST_FILE_DATE = datetime.datetime(2019, 3, 7).date()
TEST_FILE_DATE_STR = TEST_FILE_DATE.strftime('%Y-%m-%d')
INPUT_LOCAL_FULL_PATHS = {
    GTFS_FILE_NAME: join(TEST_ASSETS_DIR, 'inputs', '2019-03-07-israel-public-transportation.zip'),
    TARIFF_ZIP_NAME: join(TEST_ASSETS_DIR, 'inputs', '2019-03-07-Tariff.zip'),
    CLUSTER_TO_LINE_ZIP_NAME: join(TEST_ASSETS_DIR, 'inputs', '2019-03-07-ClusterToLine.zip'),
}
OUTPUT_FILE_TYPE = 'pkl.gz'
OUTPUT_FILE_NAMES = [
    f'route_stats_{TEST_FILE_DATE_STR}.{OUTPUT_FILE_TYPE}',
    f'trip_stats_{TEST_FILE_DATE_STR}.{OUTPUT_FILE_TYPE}'
]


def _load_gzipped_pickles(filename, expected_dir, actual_dir):
    expected_file = join(expected_dir, filename)
    actual_file = join(actual_dir, filename)

    with gzip.open(expected_file, 'rb') as f:
        expected_pickle = pickle.load(f)

    with gzip.open(actual_file, 'rb') as f:
        actual_pickle = pickle.load(f)

    return expected_pickle, actual_pickle


def test_analyze_gtfs_date():
    os.makedirs(TEST_OUTPUTS_DIR, exist_ok=True)
    analyze_gtfs_date(date=TEST_FILE_DATE,
                      local_full_paths=INPUT_LOCAL_FULL_PATHS,
                      output_folder=TEST_OUTPUTS_DIR,
                      output_file_type=OUTPUT_FILE_TYPE)

    for file_name in OUTPUT_FILE_NAMES:
        expected_df, actual_df = _load_gzipped_pickles(file_name,
                                                       join(TEST_ASSETS_DIR, 'outputs'),
                                                       TEST_OUTPUTS_DIR)
        assert expected_df.equals(actual_df)
        os.remove(join(TEST_OUTPUTS_DIR, file_name))

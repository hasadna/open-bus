import gzip
import os
import pickle
from os.path import dirname, join
from ..gtfs_utils.gtfs_stats import analyze_gtfs_date


TEST_ASSETS_DIR = join(dirname(__file__), 'assets')
TEST_OUTPUTS_DIR = join(dirname(__file__), 'outputs')
TEST_FILE_DATE = '2019-03-07'
TEST_INPUT_FILE_KEY = f'gtfs/2019/03/07/2019-03-07T01-28-07_israel-public-transportation.zip'
OUTPUT_FILE_NAMES = [
    f'{TEST_FILE_DATE}_route_stats.pkl.gz',
    f'{TEST_FILE_DATE}_trip_stats.pkl.gz'
]


def _load_gzipped_pickles(filename, expected_dir, actual_dir):
    print(join(expected_dir, filename))
    print(join(actual_dir, filename))
    with gzip.open(join(expected_dir, filename), 'rb') as f:
        expected_pickle = pickle.load(f)

    with gzip.open(join(actual_dir, filename), 'rb') as f:
        actual_pickle = pickle.load(f)

    return expected_pickle, actual_pickle


def test_handle_gtfs_file():
    os.makedirs(TEST_OUTPUTS_DIR, exist_ok=True)
    analyze_gtfs_date(date_str=TEST_FILE_DATE,
                      remote_file=TEST_INPUT_FILE_KEY,
                      crud=None,
                      output_folder=TEST_OUTPUTS_DIR,
                      gtfs_folder=join(TEST_ASSETS_DIR, 'gtfs'),
                      archive_folder=join(TEST_ASSETS_DIR, 'archive'))


    for file_name in OUTPUT_FILE_NAMES:
        expected_df, actual_df = _load_gzipped_pickles(file_name,
                                                       join(TEST_ASSETS_DIR, 'outputs'),
                                                       TEST_OUTPUTS_DIR)
        assert expected_df.equals(actual_df)
        os.remove(join(TEST_OUTPUTS_DIR, file_name))

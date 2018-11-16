from datetime import date
from gtfs_utils import gtfs_utils, gtfs_stats
import pandas as pd

ROUTE_FILENAME = 'route_stats.pkl.gz'
TRIP_FILENAME = 'trip_stats.pkl.gz'


def get_output_path(date_date: date, output_folder: str, file_name: str) -> str:
    """
    Create a path based on the givven folder, date, and file name
    :param date_date:
    :param output_folder:
    :param file_name:
    """
    date_part = date_date.strftime('%Y-%m-%d')
    folder_part = output_folder.replace('\\', '/') + '/'
    return folder_part + date_part + '_' + file_name


def save_as_pickele(obj: object, path: str) -> None:
    """
    save the given obj as a pickle in given path
    :param obj:
    :param path:
    """
    pd.to_pickle(obj, path, compression='gzip')


def add_date_column(df: pd.DataFrame, date_to_query: date) -> pd.DataFrame:
    """
    Add Categorical date column to dataframe
    :param df: DataFrame
    :param date_to_query:
    :return:
    """
    df['date'] = date_to_query.strftime('%Y-%m-%d')
    df['date'] = pd.Categorical(df.date)
    return df


def get_route_stat(date_to_query, ts) -> pd.DataFrame:
    rs = gtfs_stats.compute_route_stats_base_partridge(ts)
    return add_date_column(rs, date_to_query)


def get_trip_stat(date_to_query, feed, zones) -> pd.DataFrame:
    ts = gtfs_stats.compute_trip_stats_partridge(feed, zones)
    return add_date_column(ts, date_to_query)


def main(path_of_gtfs_zip_file: str, path_of_tariff_zip_file: str, date_to_query: date, output_folder: str):

    feed = gtfs_utils.get_partridge_feed_by_date(path_of_gtfs_zip_file, date_to_query)
    zones = gtfs_utils.get_zones_df(path_of_tariff_zip_file)

    ts = get_trip_stat(date_to_query, feed, zones)
    pickle_path = get_output_path(date_to_query, output_folder, TRIP_FILENAME)
    save_as_pickele(ts, pickle_path)

    rs = get_route_stat(date_to_query, ts)
    pickle_path = get_output_path(date_to_query, output_folder, ROUTE_FILENAME)
    save_as_pickele(rs, pickle_path)


# TODO: Add argparse for using it as CLI
if __name__ == '__main__':
    pass

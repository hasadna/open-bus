from datetime import date
from gtfs_utils import gtfs_utils, gtfs_stats


def main(path_of_gtfs_zip_file: str, path_of_tariff_zip_file: str, date_to_query: date):
    print('path_of_gtfs_zip_file: {} path_of_tariff_zip_file: {} date_to_query: {}'.format(path_of_gtfs_zip_file,
                                                                                           path_of_tariff_zip_file,
                                                                                           date_to_query))

    feed = gtfs_utils.get_partridge_feed_by_date(path_of_gtfs_zip_file, date_to_query)
    zones = gtfs_utils.get_zones_df(path_of_tariff_zip_file)

    ts = gtfs_stats.compute_trip_stats_partridge(feed, zones)

    pass

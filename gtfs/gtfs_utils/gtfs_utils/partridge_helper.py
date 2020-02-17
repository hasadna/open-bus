import datetime
import logging
from functools import lru_cache
from os.path import join, basename

import numpy as np
import pandas as pd
import partridge as ptg
from partridge import config as ptg_config

from .configuration import configuration


def create_partridge_config() -> ptg_config.nx.DiGaph:
    """Create a partridge config that convert more columns to numbers
    the configuration is based on partridge default config"""
    def to_int(series: pd.Series) -> pd.Series:
        return pd.to_numeric(series, downcast='integer')
    default_conf = ptg_config.default_config()
    converters = [
                  ('agency.txt', {
                      'agency_id': to_int,
                      'agency_name': pd.Categorical,
                  }),
                  ('calendar.txt', {
                      'service_id': to_int,
                  }),
                  ('calendar_dates.txt', {
                      'service_id': to_int,
                  }),
                  ('fare_rules.txt', {
                      'contains_id': to_int,
                      'destination_id': to_int,
                      'fare_id': to_int,
                      'origin_id': to_int,
                      'route_id': to_int,
                  }),
                  ('fare_attributes.txt', {
                      'fare_id': to_int,
                  }),
                  ('frequencies.txt', {
                      'trip_id': pd.Categorical,
                  }),
                  ('trips.txt', {
                      'direction_id': to_int,
                      'trip_id': pd.Categorical,
                      'route_id': to_int,
                      'service_id': to_int,
                      'shape_id': to_int,
                  }),
                  ('routes.txt', {
                      'agency_id': to_int,
                      'route_id': to_int,
                      'route_type': to_int,
                  }),
                  ('shapes.txt', {
                      'shape_id': to_int,
                  }),
                  ('stops.txt', {
                      'fare_id': to_int,
                      'stop_id': to_int,
                      'stop_code': to_int,
                      'zone_id': to_int,
                  }),
                  ('stop_times.txt', {
                     'stop_id': to_int,
                     'stop_sequence': to_int,
                     'pickup_type': to_int,
                     'drop_off_type': to_int,
                     'trip_id': pd.Categorical,
                  }),
                  ('transfers.txt', {
                      'from_stop_id': to_int,
                      'to_stop_id': to_int,
                  })
                  ]
    for node, fields in converters:
        node_dict = default_conf.nodes[node]
        node_converters = node_dict.setdefault('converters', {})
        node_converters.update(fields)
    return default_conf


CONF = create_partridge_config()


def get_partridge_filter_for_date(zip_path: str, date: datetime.date):
    service_ids = ptg.read_service_ids_by_date(zip_path)[date]

    return {
        'trips.txt': {
            'service_id': service_ids,
        },
    }


def get_partridge_feed_by_date(zip_path: str, date: datetime.date):
    return ptg.load_feed(zip_path,
                         view=get_partridge_filter_for_date(zip_path, date),
                         config=CONF)


def write_filtered_feed_by_date(zip_path: str, date: datetime.date, output_path: str):
    ptg.writers.extract_feed(zip_path,
                             output_path,
                             view=get_partridge_filter_for_date(zip_path, date),
                             config=CONF)


def prepare_partridge_feed(date: datetime.date,
                           gtfs_file_full_path: str,
                           filtered_feeds_directory=configuration.files.full_paths.filtered_feeds):

    if configuration.write_filtered_feed:
        filtered_gtfs_path = join(filtered_feeds_directory, basename(gtfs_file_full_path))

        logging.info(f'Filtering gtfs feed for {date} from {gtfs_file_full_path} into {filtered_gtfs_path}')
        write_filtered_feed_by_date(gtfs_file_full_path, date, filtered_gtfs_path)

        logging.info(f'Reading filtered feed for file from path {filtered_gtfs_path}')
        feed = ptg.load_feed(filtered_gtfs_path, config=CONF)
    else:
        logging.info(f'Creating daily partridge feed for {date} from {gtfs_file_full_path}')
        feed = get_partridge_feed_by_date(gtfs_file_full_path, date)

    logging.debug(f'Finished creating daily partridge feed for {date} from {gtfs_file_full_path}')
    return feed


# Copied from partridge parsers, with a deletion of the seconds field
# it is used to to parse TripIdToDate since the departure time is in HH:MM format
# Why 2^17? See https://git.io/vxB2P.
@lru_cache(maxsize=2 ** 17)
def parse_time_no_seconds(val: str) -> np.float64:
    if val is np.nan:
        return val

    val = val.strip()

    if val == "":
        return np.nan

    h, m = val.split(":")
    ssm = int(h) * 3600 + int(m) * 60

    # pandas doesn't have a NaN int, use floats
    return np.float64(ssm)


parse_time_no_seconds_column = np.vectorize(parse_time_no_seconds)

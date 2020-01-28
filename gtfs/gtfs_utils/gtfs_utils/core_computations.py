import datetime
import logging
import zipfile
from typing import List

import gtfstk
import pandas as pd
import partridge as ptg

from .aggregations import generate_trip_stats_aggregation, generate_route_stats_aggregation
from .partridge_helper import parse_time_no_seconds_column
from .constants import *


def _read_almost_valid_csv_to_df(zip_path, file_name_in_zip, real_columns):
    """ Read almost-valid csv files, which are not actually valid, while jiggling the columns a bit. """

    cols = real_columns + ['EXTRA']
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(file_name_in_zip) as file_in_zip:
            df = pd.read_csv(file_in_zip, header=None, skiprows=[0], names=cols) \
                    .drop(columns=['EXTRA'])

    return df


def _fix_trip_to_date_columns(trip_date_df: pd.DataFrame) -> None:
    """
    Parse date and time columns and fix rows where departure time is after midnight
    """
    DATE_FORMAT = '%d/%m/%Y 00:00:00'
    trip_date_df['FromDate'] = pd.to_datetime(trip_date_df.FromDate, format=DATE_FORMAT)
    trip_date_df['ToDate'] = pd.to_datetime(trip_date_df.ToDate, format=DATE_FORMAT)
    trip_date_df['departure_time'] = trip_date_df.departure_time_str.apply(parse_time_no_seconds_column)
    series = trip_date_df['departure_time'] >= 24 * 3600
    trip_date_df.loc[series, 'FromDate'] = trip_date_df[series]['FromDate'] + datetime.timedelta(days=1)
    trip_date_df.loc[series, 'ToDate'] = trip_date_df[series]['ToDate'] + datetime.timedelta(days=1)
    trip_date_df.loc[series, 'DayInWeek'] = trip_date_df[series]['DayInWeek'] + 1
    # fix dates to be from 0 o six (Sunday should be 1, Saturday 0)
    trip_date_df['DayInWeek'] = trip_date_df['DayInWeek'] % 7
    trip_date_df.loc[series, 'departure_time'] = trip_date_df[series]['departure_time'] % (24 * 3600)


def get_trip_id_to_date_df(local_file_path: str, date: datetime.date) -> pd.DataFrame:
    """
    returns the TripIdToDate information that matches the given date
    :param local_file_path: The path if the zip file
    :param date: The date to filter by
    :return: A DataFrame with the columns `route_id`, `trip_id_to_date` and `start_time`
    """
    trip_id_to_date_cols = ['route_id', 'OfficeLineId', 'Direction', 'LineAlternative', 'FromDate',
                            'ToDate', 'trip_id_to_date', 'DayInWeek', 'departure_time_str']
    trip_date_df = _read_almost_valid_csv_to_df(local_file_path, TRIP_ID_TO_DATE_TXT_NAME, trip_id_to_date_cols)
    _fix_trip_to_date_columns(trip_date_df)
    # filter to a specific date
    trip_date_df = trip_date_df[(trip_date_df['FromDate'] <= pd.Timestamp(date)) &
                                (trip_date_df['ToDate'] >= pd.Timestamp(date)) &
                                # Fix date.isoweekday to match israel counting (Sunday is 1, Saturday=0)
                                (trip_date_df['DayInWeek'] == ((date.isoweekday() + 1) % 7))
                                ]
    # remove all columns except 'route_id' and 'trip_id_to_date'
    trip_date_df = trip_date_df[['route_id', 'trip_id_to_date', 'departure_time']]
    # change column type because feed returns route_id as object (and not int64)
    trip_date_df = trip_date_df.assign(route_id=trip_date_df.route_id.astype(str))
    return trip_date_df


def get_zones_df(local_tariff_zip_path):
    tariff_cols = ['ShareCode', 'ShareCodeDesc', 'ZoneCodes', 'Daily', 'Weekly', 'Monthly', 'FromDate', 'ToDate']
    tariff_df = _read_almost_valid_csv_to_df(local_tariff_zip_path, TARIFF_TXT_NAME, tariff_cols)

    reform_cols = ['StationId', 'ReformZoneCode', 'FromDate', 'ToDate']
    reform_df = _read_almost_valid_csv_to_df(local_tariff_zip_path, TARIFF_TO_REFORM_ZONE, reform_cols)

    # remove ShareCodes which contain multiple zones  e.g. גוש דן מורחב
    tariff_df = (tariff_df[~ tariff_df.ZoneCodes.str.contains(';')]
                 .rename(columns={'ShareCodeDesc': 'zone_name',
                                  'ZoneCodes': 'zone_id'}))
    rs = reform_df[['StationId', 'ReformZoneCode']].drop_duplicates().applymap(str).set_index('StationId').iloc[:, 0]

    ts = (tariff_df[['zone_id', 'zone_name']].drop_duplicates().set_index('zone_id').iloc[:, 0])
    zones = rs.map(ts).reset_index().rename(columns={'StationId': 'stop_code', 'ReformZoneCode': 'zone_name'})
    return zones


def get_clusters_df(local_cluster_zip_path):
    cluster_cols = ['OperatorName', 'OfficeLineId', 'OperatorLineId', 'ClusterName', 'FromDate', 'ToDate', 'ClusterId',
                    'LineType', 'LineTypeDesc', 'ClusterSubDesc']

    clusters_df = _read_almost_valid_csv_to_df(local_cluster_zip_path, CLUSTER_TO_LINE_TXT_NAME, cluster_cols)

    clusters_df = clusters_df.rename(columns={
        'ClusterId': 'cluster_id',
        'ClusterName': 'cluster_name',
        'ClusterSubDesc': 'cluster_sub_desc',
        'LineType': 'line_type',
        'LineTypeDesc': 'line_type_desc',
        'OfficeLineId': 'route_mkt'
    }).drop(columns=['OperatorName', 'OperatorLineId', 'FromDate', 'ToDate'])

    return clusters_df


def compute_trip_stats(feed: ptg.feed,
                       zones: pd.DataFrame,
                       clusters: pd.DataFrame,
                       trip_to_date: pd.DataFrame,
                       date: datetime.date,
                       source_files_base_name: List[str]) -> pd.DataFrame:
    """
    :param feed: Partridge feed for the specific date
    :param zones: DataFrame with stop_code to zone_name mapping
    :param trip_to_date: trip_id_to_date information to match with the feed data
    :param date: The original schedule date
    :param source_files_base_name: The original zips the data is based on (GTFS, Tariff, etc.)
    :returns: A DataFrame with columns as described below

    Trip stats table has the following columns:

    - ``agency_id`` - Agency identifier, as specified in `agency.txt` file.
    - ``agency_name`` - The full name of the agency, as specified in `agency.txt` file.
    - ``all_stop_code`` - All stop codes (as specified in `stops.txt` file), separated by semicolons.
    - ``all_stop_desc_city`` - Cities of all stops of the trip (as described in `stop_desc` field in `stops.txt` \
        file), separated by semicolons.
    - ``all_stop_id`` - All stop identifiers (as specified in `stops.txt` file), separated by \
        semicolons.
    - ``all_stop_latlon`` - All stop waypoints (`stop_lat` and `stop_lon` as specified in `stops.txt` file), formatted \
        as `lat,lon` and separated by semicolons.
    - ``cluster_id`` - Cluster code, as in `ClusterId` in `ClusterToLine` file.
    - ``cluster_name`` - The name of the cluster to which the line belongs, as in `ClusterName` in `ClusterToLine` file.
    - ``cluster_sub_desc`` - A sub-cluster name to which the line is associated, as in `ClusterSubDesc` in \
        `ClusterToLine` file.
    - ``date`` - The original schedule date
    - ``direction_id`` - Indicates the direction of travel for a trip, as specified in `trips.txt` file.
    - ``distance`` - The full travel distance of the trip in meters, which is the maximal `shape_dist_traveled`, as \
        specified in `stop_times.txt` file.
    - ``duration`` - Duration of the trip in hours
    - ``end_stop_city`` - The city of the last stop of the trip, as described in `stop_desc` field in `stops.txt` file.
    - ``end_stop_code`` - Stop code of the last stop of the trip
    - ``end_stop_desc`` - The description of the last stop of the trip, as described as `stop_desc` field in \
        `stops.txt` file.
    - ``end_stop_id`` - Stop ID of the last stop of the trip
    - ``end_stop_lat`` - Latitude of the last stop of the trip
    - ``end_stop_lon`` - Longitude of the last stop of the trip
    - ``end_stop_name`` - Stop name of the last stop of the trip
    - ``end_time`` - Departure time of the last stop of the trip
    - ``end_zone`` - Zone name of the last stop of the trip
    - ``source_files`` - The original the data is based on (GTFS, Tariff, etc.)
    - ``is_loop`` - 1 if the start and end stop are less than 400m apart, otherwise 0
    - ``line_type`` - Line type code, as in `LineType` in `ClusterToLine` file.
    - ``line_type_desc`` - Line type description, as in `LineTypeDesc` in `ClusterToLine` file. \
        The options for this fields are:
        * "עירוני" - Urban
        * "בינעירוני" - Intercity
        * "אזורי" - Regional
    - ``num_stops`` - Number of stops in trip
    - ``num_zones`` - Number of zones where the trip stops are. Zones are defined in the files in `Tariff.zip`.
    - ``num_zones_missing`` - Number of stops whose identifier is missing from the files in `Tariff.zip`.
    - ``route_alternative`` - A route's alternative identifier. Constructs a route identifier together \
        with ``route_direction`` and ``route_mkt``.
    - ``route_direction`` - A route's direction identifier. Constructs a route identifier together \
        with ``route_alternative`` and ``route_mkt``.
    - ``route_id`` - Route identifier, as specified in `routes.txt` file.
    - ``route_long_name`` - The full name of a route, as specified in `routes.txt` file.
    - ``route_mkt`` - MOT Line's 5-digit catalog number ("`מק"ט`"), a unique number at the line level, \
        but not unique at the alternative level. Constructs a route identifier together \
        with ``route_direction`` and ``route_alternative``.
    - ``route_short_name`` - The short name of a route, as specified in `routes.txt` file.
    - ``route_type`` - The type of transportation used on a route, as specified in \
        `routes.txt`. In Israel, MOT uses:
        * 0 for light train (Jerusalem Light Rail)
        * 2 for train (Israel Railways)
        * 3 for bus
        * 715 for Flexible Service Line ("קו בשירות גמיש")
    - ``shape_id`` - Shape identifier, as specified in `shapes.txt` file.
    - ``speed`` - Average speed of the trip in meters per hour (calculated as `distance/duration`).
    - ``start_stop_city`` - The city of the first stop of the trip, as specified in `stop_desc` field in `stops.txt` \
        file.
    - ``start_stop_code`` - Stop code of the first stop of the trip
    - ``start_stop_desc`` - The description of the first stop of the trip, as described as `stop_desc` field in \
        `stops.txt` file.
    - ``start_stop_id`` - Stop ID of the first stop of the trip
    - ``start_stop_lat`` - Latitude of the first stop of the trip
    - ``start_stop_lon`` - Longitude of the first stop of the trip
    - ``start_stop_name`` - Stop name of the first stop of the trip
    - ``start_time`` - Departure time of the first stop of the trip
    - ``start_zone`` - Zone name of the first stop of the trip
    - ``trip_id`` - Trip identifier, as specified in `trips.txt` file.
    """

    source_files_str = '\n'.join(source_files_base_name)
    logging.info((f'Starting compute_trip_stats for {date} from files: \n' 
                  f'{source_files_str}'))

    f = feed.trips
    f = (f[['route_id', 'trip_id', 'direction_id', 'shape_id']]
         .merge(feed.routes[['route_id', 'route_short_name', 'route_long_name',
                             'route_type', 'agency_id', 'route_desc']])
         .merge(feed.agency[['agency_id', 'agency_name']], how='left', on='agency_id')
         .merge(feed.stop_times)
         .merge(feed.stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'stop_code', 'stop_desc']])
         .merge(zones, how='left')
         .sort_values(['trip_id', 'stop_sequence'])
         )

    # parse route_desc
    f[['route_mkt', 'route_direction', 'route_alternative']] = f['route_desc'].str.split('-', expand=True)
    f = f.drop('route_desc', axis=1)
    f['route_mkt'] = f['route_mkt'].astype(int)

    f = f.merge(clusters, how='left', on='route_mkt')

    # parse stop_desc
    stop_desc_fields = {'street': 'רחוב',
                        'city': 'עיר',
                        'platform': 'רציף',
                        'floor': 'קומה'}

    stop_desc_prefix = 'stop_desc_'

    STOP_DESC_RE = ''
    for n, fld in stop_desc_fields.items():
        STOP_DESC_RE += fld + f':(?P<{stop_desc_prefix + n}>.*)'

    sd = f.stop_desc.str.extract(STOP_DESC_RE).apply(lambda x: x.str.strip())
    f = pd.concat([f, sd], axis=1)

    g = f.groupby('trip_id')
    aggregation = generate_trip_stats_aggregation(feed)
    h = g.apply(aggregation)
    h['distance'] = g.shape_dist_traveled.max()

    # Reset index and compute final stats
    h = h.reset_index()
    h['speed'] = h['distance'] / h['duration'] / 1000
    h[['start_time', 'end_time']] = (
        h[['start_time', 'end_time']].applymap(
            lambda x: gtfstk.helpers.timestr_to_seconds(x, inverse=True))
    )

    # h = h.merge(trip_to_date, how='inner', on=['route_id', 'start_time'])
    h['date'] = date
    h['date'] = pd.Categorical(h['date'])
    h['source_files'] = ';'.join(source_files_base_name)

    logging.debug((f'finished compute_trip_stats for {date} from: \n' 
                   f'{source_files_str}'))

    return h


def compute_route_stats(trip_stats_subset: pd.DataFrame,
                        date: datetime.date,
                        source_files_base_name: List[str],
                        headway_start_time: str = '07:00:00',
                        headway_end_time: str = '19:00:00') -> pd.DataFrame:
    """
    Compute stats for the given subset of trips stats.

    :param trip_stats_subset: Subset of the output of :func:`compute_trip_stats`
    :param date: The original schedule date
    :param source_files_base_name: The original zips the data is based on (GTFS, Tariff, etc.)
    :param headway_start_time: HH:MM:SS time string indicating the start time for computing \
    headway stats
    :param headway_end_time: HH:MM:SS time string indicating the end time for computing headway \
    stats
    :returns: A DataFrame with columns as described below

    Route stats table has the following columns:

    - ``agency_id`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``agency_name`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``all_start_time`` - All of the start times (formatted as HH:MM:SS) in which the trips in \
        the route start, separated by semicolons
    - ``all_stop_code`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``all_stop_desc_city`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``all_stop_id`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``all_stop_latlon`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``all_stop_name`` - Names of all stops of the trip (as described in `stop_name` field in \
        `stops.txt` file), separated by semicolons.
    - ``all_trip_id`` - All of the identifiers (``trip_id``, as specified in `trips.txt` file) of \
        the trips in the route, separated by semicolons
    - ``cluster_id`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``cluster_name`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``cluster_sub_desc`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``date`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``end_stop_city`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``end_stop_desc`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``end_stop_id`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``end_stop_lat`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``end_stop_lon`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``end_stop_name`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``end_time`` - Same as in :func:`gtfs_utils.compute_trip_stats`, referring to the last trip \
    of the route
    - ``end_zone`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``source_files`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``is_bidirectional`` - 1 if the route has trips in both directions, otherwise 0
    - ``is_loop`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``line_type`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``line_type_desc`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``max_headway`` - The maximal duration (in minutes) between trip starts on the route between \
        ``headway_start_time`` and ``headway_end_time``
    - ``mean_headway`` - The mean duration (in minutes) between trip starts on the route between \
        ``headway_start_time`` and ``headway_end_time``
    - ``mean_trip_distance`` - The full travel distance of each trip on the route in meters, which \
        is the maximal `shape_dist_traveled`, as specified in `stop_times.txt` file (calculated as \
        `service_distance/num_trips`)
    - ``mean_trip_duration`` - Duration of each trip on the route in hours (calculated as \
        `service_duration/num_trips`)
    - ``min_headway`` - The minimal duration (in minutes) between trip starts on the route between \
        ``headway_start_time`` and ``headway_end_time``
    - ``num_stops`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``num_trip_ends`` - Number of trips on the route in the subset with non-null end times before 23:59:59
    - ``num_trip_starts`` - Number of trips on the route in the subset with non-null start times
    - ``num_trips`` - Number of trips on the route in the subset
    - ``num_zones`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``num_zones_missing`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``peak_end_time`` - End time of first longest period during which the peak number of trips \
        (``peak_num_trips``) occurs
    - ``peak_num_trips`` - Maximal number of simultaneous trips in the service (for a given direction)
    - ``peak_start_time`` - Start time of first longest period during which the peak number of trips \
        (``peak_num_trips``) occurs
    - ``route_alternative`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``route_direction`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``route_id`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``route_long_name`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``route_mkt`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``route_short_name`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``route_type`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``service_distance`` - The full travel distance of all trips on the route in meters, which \
        is the maximal `shape_dist_traveled`, as specified in `stop_times.txt` file.
    - ``service_duration`` - Total duration of all trips on the route in hours
    - ``service_speed`` - Average speed each trip on the route in km/h
    - ``start_stop_city`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``start_stop_desc`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``start_stop_id`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``start_stop_lat`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``start_stop_lon`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``start_stop_name`` - Same as in :func:`gtfs_utils.compute_trip_stats`
    - ``start_time`` - Same as in :func:`gtfs_utils.compute_trip_stats`, referring to the first \
     trip of the route
    - ``start_zone`` -  Same as in :func:`gtfs_utils.compute_trip_stats`

    If ``trip_stats_subset`` is empty, return an empty DataFrame.

    """
    source_files_str = ';'.join(source_files_base_name)
    logging.info(f'Starting compute_route_stats from trip stats result')

    f = trip_stats_subset.copy()
    f[['start_time', 'end_time']] = f[['start_time', 'end_time']].applymap(gtfstk.helpers.timestr_to_seconds)

    aggregation = generate_route_stats_aggregation(headway_start_time, headway_end_time)
    g = f.groupby('route_id').apply(aggregation).reset_index()

    # Compute a few more stats
    g['service_speed'] = g['service_distance'] / g['service_duration']
    g['mean_trip_distance'] = g['service_distance'] / g['num_trips']
    g['mean_trip_duration'] = g['service_duration'] / g['num_trips']

    # Convert route times to time strings
    time_cols = ['start_time', 'end_time', 'peak_start_time', 'peak_end_time']
    g[time_cols] = g[time_cols].applymap(lambda x: gtfstk.helpers.timestr_to_seconds(x, inverse=True))

    # Convert m/h to km/h
    g['service_speed'] = g.service_speed / 1000

    g = g[[
        'route_id', 'route_short_name', 'agency_id', 'agency_name', 'route_long_name', 'route_type', 'route_mkt',
        'route_direction', 'route_alternative', 'num_trips', 'num_trip_starts', 'num_trip_ends', 'is_loop',
        'is_bidirectional', 'start_time', 'end_time', 'max_headway', 'min_headway', 'mean_headway',
        'peak_num_trips', 'peak_start_time', 'peak_end_time', 'service_distance', 'service_duration', 'service_speed',
        'mean_trip_distance', 'mean_trip_duration', 'start_stop_id', 'end_stop_id', 'start_stop_name', 'end_stop_name',
        'start_stop_city', 'end_stop_city', 'start_stop_desc', 'end_stop_desc', 'start_stop_lat', 'start_stop_lon',
        'end_stop_lat', 'end_stop_lon', 'num_stops', 'start_zone', 'end_zone', 'num_zones', 'num_zones_missing',
        'all_stop_latlon', 'all_stop_code', 'all_stop_id', 'all_stop_desc_city', 'all_start_time', 'all_trip_id',
        'all_stop_name', 'line_type', 'line_type_desc', 'cluster_id', 'cluster_name', 'cluster_sub_desc',
    ]]

    g['date'] = date
    g['date'] = pd.Categorical(g['date'])
    g['source_files'] = source_files_str

    logging.debug(f'Finished compute_route_stats from trip stats result')

    return g

import pandas as pd
import numpy as np
import partridge as ptg
import zipfile
import gtfstk
from collections import OrderedDict
from constants import *


def get_zones_df(local_tariff_zip_path):
    # not a true csv, so we need to jiggle it a bit, hence the 'EXTRA' field
    tariff_cols = ['ShareCode', 'ShareCodeDesc', 'ZoneCodes', 'Daily', 'Weekly', 'Monthly', 'FromDate', 'ToDate',
                   'EXTRA']
    reform_cols = ['StationId', 'ReformZoneCode', 'FromDate', 'ToDate', 'EXTRA']
    with zipfile.ZipFile(local_tariff_zip_path) as zf:
        tariff_df = (pd.read_csv(zf.open(TARIFF_TXT_NAME), header=None, skiprows=[0], names=tariff_cols)
                     .drop(columns=['EXTRA']))
        reform_df = (pd.read_csv(zf.open(TARIFF_TO_REFORM_ZONE), header=None, skiprows=[0], names=reform_cols)
                     .drop(columns=['EXTRA']))

    # remove ShareCodes which contain multiple zones  e.g. גוש דן מורחב
    tariff_df = (tariff_df[~ tariff_df.ZoneCodes.str.contains(';')]
                 .rename(columns={'ShareCodeDesc': 'zone_name',
                                  'ZoneCodes': 'zone_id'}))
    rs = reform_df[['StationId', 'ReformZoneCode']].drop_duplicates().applymap(str).set_index('StationId').iloc[:, 0]

    ts = (tariff_df[['zone_id', 'zone_name']].drop_duplicates().set_index('zone_id').iloc[:, 0])
    zones = rs.map(ts).reset_index().rename(columns={'StationId': 'stop_code', 'ReformZoneCode': 'zone_name'})
    return zones


def get_partridge_feed_by_date(zip_path, date):
    service_ids_by_date = ptg.read_service_ids_by_date(zip_path)  # , encoding='utf-8')
    service_ids = service_ids_by_date[date]

    feed = ptg.feed(zip_path, view={
        'trips.txt': {
            'service_id': service_ids,
        },
    },
                    # encoding='utf-8' # CUSTOM VERSION, NOT YET PUSHED
                    )
    return feed


def write_filtered_feed_by_date(zip_path, date, output_path):
    service_ids_by_date = ptg.read_service_ids_by_date(zip_path)  # , encoding='utf-8')
    service_ids = service_ids_by_date[date]

    ptg.writers.extract_feed(zip_path, output_path, {
        'trips.txt': {
            'service_id': service_ids,
        },
    })


def compute_trip_stats_partridge(feed, zones):
    """
    Parameters
    ----------
    feed : partridge feed
    zones: DataFrame with stop_code to zone_name mapping

    Returns
    -------
    DataFrame with the following columns:

    - ``'trip_id'``
    - ``'route_id'``
    - ``'route_short_name'``
    - ``'route_short_name'``
    - ``'agency_id'``
    - ``'agency_name'``
    - ``'route_long_name'``
    - ``'route_type'``
    - ``'direction_id'``
    - ``'shape_id'``
    - ``'num_stops'``: number of stops on trip
    - ``'start_time'``: first departure time of the trip
    - ``'end_time'``: last departure time of the trip
    - ``'start_stop_id'``: stop ID of the first stop of the trip
    - ``'end_stop_id'``: stop ID of the last stop of the trip
    - ``'start_stop_name'``: stop name of the first stop of the trip
    - ``'end_stop_name'``: stop name of the last stop of the trip
    - ``'start_stop_code'``: stop code of the first stop of the trip
    - ``'end_stop_code'``: stop code of the last stop of the trip
    - ``'start_stop_lat'``: ``start_stop_lat`` of the first stop of the trip
    - ``'start_stop_lon'``: ``start_stop_lon`` of the first stop of the trip
    - ``'end_stop_lat'``: ``end_stop_lat`` of the last stop of the trip
    - ``'end_stop_lon'``: ``end_stop_lon`` of the last stop of the trip
    - ``'start_zone'``: zone name of the first stop of the trip
    - ``'end_zone'``: zone name of the last stop of the trip
    - ``'num_zones'``:  ``num_zones`` of the first stop of the trip
    - ``'num_zones_missing'``:  ``num_zones_missing`` of the first stop of the trip
    - ``'is_loop'``: 1 if the start and end stop are less than 400m apart and
      0 otherwise
    - ``'distance'``: distance of the trip in ``feed.dist_units``;
      contains all ``np.nan`` entries if ``feed.shapes is None``
    - ``'duration'``: duration of the trip in hours
    - ``'speed'``: distance/duration

    TODO: this is not true here, we're only using shape_dist_traveled
    TODO: implement or drop from docs
    If ``feed.stop_times`` has a ``shape_dist_traveled`` column with at
    least one non-NaN value and ``compute_dist_from_shapes == False``,
    then use that column to compute the distance column.
    Else if ``feed.shapes is not None``, then compute the distance
    column using the shapes and Shapely.
    Otherwise, set the distances to NaN.

    If route IDs are given, then restrict to trips on those routes.

    Notes
    -----
    - Assume the following feed attributes are not ``None``:

        * ``feed.trips``
        * ``feed.routes``
        * ``feed.stop_times``
        * ``feed.shapes`` (optionally)
        * Those used in :func:`.stops.build_geometry_by_stop`

    - Calculating trip distances with ``compute_dist_from_shapes=True``
      seems pretty accurate.  For example, calculating trip distances on
      `this Portland feed
      <https://transitfeeds.com/p/trimet/43/1400947517>`_
      using ``compute_dist_from_shapes=False`` and
      ``compute_dist_from_shapes=True``,
      yields a difference of at most 0.83km from the original values.

    """
    f = feed.trips
    f = (f[['route_id', 'trip_id', 'direction_id', 'shape_id']]
         .merge(feed.routes[['route_id', 'route_short_name', 'route_long_name',
                             'route_type', 'agency_id', 'route_desc']])
         .merge(feed.agency[['agency_id', 'agency_name']], how='left', on='agency_id')
         .merge(feed.stop_times)
         .merge(feed.stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'stop_code', 'stop_desc']])
         .merge(zones, how='left')
         .sort_values(['trip_id', 'stop_sequence'])
         # .assign(departure_time=lambda x: x['departure_time'].map(
         #    hp.timestr_to_seconds)
         #       )
         )

    # parse route_desc
    f[['route_mkt', 'route_direction', 'route_alternative']] = f['route_desc'].str.split('-', expand=True)
    f = f.drop('route_desc', axis=1)

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

    # get geometry by stop for distance measurement
    geometry_by_stop = gtfstk.build_geometry_by_stop(feed, use_utm=True)

    g = f.groupby('trip_id')

    def my_agg(group):
        d = OrderedDict()
        d['route_id'] = group['route_id'].iat[0]
        d['route_short_name'] = group['route_short_name'].iat[0]
        d['route_long_name'] = group['route_long_name'].iat[0]
        d['route_mkt'] = group['route_mkt'].iat[0]
        d['route_direction'] = group['route_direction'].iat[0]
        d['route_alternative'] = group['route_alternative'].iat[0]
        d['agency_id'] = group['agency_id'].iat[0]
        d['agency_name'] = group['agency_name'].iat[0]
        d['route_type'] = group['route_type'].iat[0]
        d['direction_id'] = group['direction_id'].iat[0]
        d['shape_id'] = group['shape_id'].iat[0]
        d['num_stops'] = group.shape[0]
        d['start_time'] = group['departure_time'].iat[0]
        d['end_time'] = group['departure_time'].iat[-1]
        d['start_stop_id'] = group['stop_id'].iat[0]
        d['end_stop_id'] = group['stop_id'].iat[-1]
        d['start_stop_code'] = group['stop_code'].iat[0]
        d['end_stop_code'] = group['stop_code'].iat[-1]
        d['start_stop_name'] = group['stop_name'].iat[0]
        d['end_stop_name'] = group['stop_name'].iat[-1]
        d['start_stop_desc'] = group['stop_desc'].iat[0]
        d['end_stop_desc'] = group['stop_desc'].iat[-1]
        d['start_stop_lat'] = group['stop_lat'].iat[0]
        d['start_stop_lon'] = group['stop_lon'].iat[0]
        d['end_stop_lat'] = group['stop_lat'].iat[-1]
        d['end_stop_lon'] = group['stop_lon'].iat[-1]
        d['start_stop_city'] = group['stop_desc_city'].iat[0]
        d['end_stop_city'] = group['stop_desc_city'].iat[-1]
        d['start_zone'] = group['zone_name'].iat[0]
        d['end_zone'] = group['zone_name'].iat[-1]
        d['num_zones'] = group.zone_name.nunique()
        d['num_zones_missing'] = group.zone_name.isnull().sum()
        dist = geometry_by_stop[d['start_stop_id']].distance(
            geometry_by_stop[d['end_stop_id']])
        d['is_loop'] = int(dist < 400)
        d['duration'] = (d['end_time'] - d['start_time']) / 3600

        d['all_stop_latlon'] = ';'.join(str(x) + ',' + str(y) for x, y in
                                        zip(group['stop_lat'].tolist(), group['stop_lon'].tolist()))

        d['all_stop_code'] = ';'.join(group['stop_code'].tolist())
        d['all_stop_id'] = ';'.join(group['stop_id'].tolist())
        d['all_stop_desc_city'] = ';'.join(group['stop_desc_city'].tolist())

        return pd.Series(d)

    h = g.apply(my_agg)
    h['distance'] = g.shape_dist_traveled.max()

    # Reset index and compute final stats
    h = h.reset_index()
    h['speed'] = h['distance'] / h['duration'] / 1000
    h[['start_time', 'end_time']] = (
        h[['start_time', 'end_time']].applymap(
            lambda x: gtfstk.helpers.timestr_to_seconds(x, inverse=True))
    )
    return h


def get_active_trips_df(trip_times):
    """
    Count the number of trips in ``trip_times`` that are active
    at any given time.

    Parameters
    ----------
    trip_times : DataFrame
        Contains columns

        - start_time: start time of the trip in seconds past midnight
        - end_time: end time of the trip in seconds past midnight

    Returns
    -------
    Series
        index is times from midnight when trips start and end, values are number of active trips for that time

    """
    active_trips = pd.concat([pd.Series(1, trip_times.start_time),  # departed add 1
                              pd.Series(-1, trip_times.end_time)  # arrived subtract 1
                              ]).groupby(level=0, sort=True).sum().cumsum().ffill()
    return active_trips


def compute_route_stats_base_partridge(trip_stats_subset,
                                       headway_start_time='07:00:00',
                                       headway_end_time='19:00:00',
                                       *,
                                       split_directions=False):
    """
    Compute stats for the given subset of trips stats.

    Parameters
    ----------
    trip_stats_subset : DataFrame
        Subset of the output of :func:`.trips.compute_trip_stats`
    split_directions : boolean
        If ``True``, then separate the stats by trip direction (0 or 1);
        otherwise aggregate trips visiting from both directions.
        Default: ``False``
    headway_start_time : string
        HH:MM:SS time string indicating the start time for computing
        headway stats
        Default: ``'07:00:00'``
    headway_end_time : string
        HH:MM:SS time string indicating the end time for computing
        headway stats.
        Default: ``'19:00:00'``

    Returns
    -------
    DataFrame
        Columns are

        - ``'route_id'``
        - ``'route_short_name'``
        - ``'agency_id'``
        - ``'agency_name'``
        - ``'route_long_name'``
        - ``'route_type'``
        - ``'direction_id'``: 1/0
        - ``'num_trips'``: number of trips on the route in the subset
        - ``'num_trip_starts'``: number of trips on the route with
          nonnull start times
        - ``'num_trip_ends'``: number of trips on the route with nonnull
          end times that end before 23:59:59
        - ``'is_loop'``: 1 if at least one of the trips on the route has
          its ``is_loop`` field equal to 1; 0 otherwise
        - ``'is_bidirectional'``: 1 if the route has trips in both
          directions; 0 otherwise
        - ``'start_time'``: start time of the earliest trip on the route
        - ``'end_time'``: end time of latest trip on the route
        - ``'max_headway'``: maximum of the durations (in minutes)
          between trip starts on the route between
          ``headway_start_time`` and ``headway_end_time`` on the given
          dates
        - ``'min_headway'``: minimum of the durations (in minutes)
          mentioned above
        - ``'mean_headway'``: mean of the durations (in minutes)
          mentioned above
        - ``'peak_num_trips'``: maximum number of simultaneous trips in
          service (for the given direction, or for both directions when
          ``split_directions==False``)
        - ``'peak_start_time'``: start time of first longest period
          during which the peak number of trips occurs
        - ``'peak_end_time'``: end time of first longest period during
          which the peak number of trips occurs
        - ``'service_duration'``: total of the duration of each trip on
          the route in the given subset of trips; measured in hours
        - ``'service_distance'``: total of the distance traveled by each
          trip on the route in the given subset of trips; measured in
          whatever distance units are present in ``trip_stats_subset``;
          contains all ``np.nan`` entries if ``feed.shapes is None``
        - ``'service_speed'``: service_distance/service_duration;
          measured in distance units per hour
        - ``'mean_trip_distance'``: service_distance/num_trips
        - ``'mean_trip_duration'``: service_duration/num_trips
        - ``'start_stop_id'``: ``start_stop_id`` of the first trip for the route
        - ``'end_stop_id'``: ``end_stop_id`` of the first trip for the route
        - ``'start_stop_lat'``: ``start_stop_lat`` of the first trip for the route
        - ``'start_stop_lon'``: ``start_stop_lon`` of the first trip for the route
        - ``'end_stop_lat'``: ``end_stop_lat`` of the first trip for the route
        - ``'end_stop_lon'``: ``end_stop_lon`` of the first trip for the route
        - ``'num_stops'``: ``num_stops`` of the first trip for the route
        - ``'start_zone'``: ``start_zone`` of the first trip for the route
        - ``'end_zone'``: ``end_zone`` of the first trip for the route
        - ``'num_zones'``:  ``num_zones`` of the first trip for the route
        - ``'num_zones_missing'``:  ``num_zones_missing`` of the first trip for the route

        TODO: actually implement split_directions
        If not ``split_directions``, then remove the
        direction_id column and compute each route's stats,
        except for headways, using
        its trips running in both directions.
        In this case, (1) compute max headway by taking the max of the
        max headways in both directions; (2) compute mean headway by
        taking the weighted mean of the mean headways in both
        directions.

        If ``trip_stats_subset`` is empty, return an empty DataFrame.

    """
    f = trip_stats_subset.copy()
    f[['start_time', 'end_time']] = f[['start_time', 'end_time']].applymap(gtfstk.helpers.timestr_to_seconds)

    headway_start = gtfstk.helpers.timestr_to_seconds(headway_start_time)
    headway_end = gtfstk.helpers.timestr_to_seconds(headway_end_time)

    def compute_route_stats(group):
        d = OrderedDict()
        keys = [
            'route_short_name', 'route_long_name', 'route_mkt', 'route_direction',
            'route_alternative', 'agency_id', 'agency_name', 'route_type', 'start_stop_id',
            'end_stop_id', 'start_stop_name', 'end_stop_name', 'start_stop_desc', 'end_stop_desc',
            'start_stop_lat', 'start_stop_lon', 'end_stop_lat', 'end_stop_lon', 'start_stop_city',
            'end_stop_city', 'num_stops', 'start_zone', 'end_zone', 'num_zones',
            'num_zones_missing', 'all_stop_latlon', 'all_stop_code', 'all_stop_id',
            'all_stop_desc_city'
        ]
        for key in keys:
            d[key] = group[key].iat[0]


        d['num_trips'] = group.shape[0]
        d['num_trip_starts'] = group['start_time'].count()
        d['num_trip_ends'] = group.loc[
            group['end_time'] < 24 * 3600, 'end_time'].count()
        d['is_loop'] = int(group['is_loop'].any())
        d['is_bidirectional'] = int(group['direction_id'].unique().size > 1)
        d['start_time'] = group['start_time'].min()
        d['end_time'] = group['end_time'].max()

        # Compute headway stats
        headways = np.array([])
        for direction in [0, 1]:
            stimes = group[group['direction_id'] == direction][
                'start_time'].values
            stimes = sorted([stime for stime in stimes
                             if headway_start <= stime <= headway_end])
            headways = np.concatenate([headways, np.diff(stimes)])
        if headways.size:
            d['max_headway'] = np.max(headways) / 60  # minutes
            d['min_headway'] = np.min(headways) / 60  # minutes
            d['mean_headway'] = np.mean(headways) / 60  # minutes
        else:
            d['max_headway'] = np.nan
            d['min_headway'] = np.nan
            d['mean_headway'] = np.nan

        # Compute peak num trips
        active_trips = get_active_trips_df(group[['start_time', 'end_time']])
        times, counts = active_trips.index.values, active_trips.values
        start, end = gtfstk.helpers.get_peak_indices(times, counts)
        d['peak_num_trips'] = counts[start]
        d['peak_start_time'] = times[start]
        d['peak_end_time'] = times[end]

        d['service_distance'] = group['distance'].sum()
        d['service_duration'] = group['duration'].sum()


        d['all_start_time'] = ';'.join([gtfstk.helpers.timestr_to_seconds(x, inverse=True)
                                        for x in group['start_time'].tolist()])
        d['all_trip_id'] = ';'.join(group['trip_id'].tolist())
        return pd.Series(d)

    g = f.groupby('route_id').apply(
        compute_route_stats).reset_index()

    # Compute a few more stats
    g['service_speed'] = g['service_distance'] / g['service_duration']
    g['mean_trip_distance'] = g['service_distance'] / g['num_trips']
    g['mean_trip_duration'] = g['service_duration'] / g['num_trips']

    # Convert route times to time strings
    time_cols = ['start_time', 'end_time', 'peak_start_time', 'peak_end_time']
    g[time_cols] = g[time_cols].applymap(lambda x: gtfstk.helpers.timestr_to_seconds(x, inverse=True))

    g['service_speed'] = g.service_speed / 1000

    g = g[['route_id', 'route_short_name', 'agency_id', 'agency_name',
           'route_long_name', 'route_type', 'route_mkt', 'route_direction', 'route_alternative',
           'num_trips', 'num_trip_starts',
           'num_trip_ends', 'is_loop', 'is_bidirectional', 'start_time',
           'end_time', 'max_headway', 'min_headway', 'mean_headway',
           'peak_num_trips', 'peak_start_time', 'peak_end_time',
           'service_distance', 'service_duration', 'service_speed',
           'mean_trip_distance', 'mean_trip_duration', 'start_stop_id',
           'end_stop_id', 'start_stop_name', 'end_stop_name',
           'start_stop_city', 'end_stop_city',
           'start_stop_desc', 'end_stop_desc',
           'start_stop_lat', 'start_stop_lon', 'end_stop_lat',
           'end_stop_lon', 'num_stops', 'start_zone', 'end_zone',
           'num_zones', 'num_zones_missing',
           'all_stop_latlon', 'all_stop_code', 'all_stop_id', 'all_stop_desc_city', 'all_start_time', 'all_trip_id',
           ]]

    return g

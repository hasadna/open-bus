from collections import OrderedDict
import pandas as pd
import numpy as np
import gtfstk


def generate_trip_stats_aggregation(feed):

    # get geometry by stop for distance measurement
    geometry_by_stop = gtfstk.build_geometry_by_stop(feed, use_utm=True)

    def trip_stats_aggregation(group):
        d = OrderedDict()

        keys = [
            'route_id', 'route_short_name', 'route_long_name', 'route_mkt', 'route_direction',
            'route_alternative', 'agency_id', 'agency_name', 'route_type', 'direction_id',
            'shape_id'
        ]
        for key in keys:
            d[key] = group[key].iat[0]

        d['num_stops'] = group.shape[0]

        keys_for_start_and_end = [
            'departure_time', 'stop_id', 'stop_code', 'stop_name', 'stop_desc', 'stop_lat',
            'stop_lon', 'stop_desc_city', 'zone_name'
        ]
        for key in keys_for_start_and_end:
            d[f'start_{key}'] = group[key].iat[0]
            d[f'end_{key}'] = group[key].iat[-1]

        # Key is the original name, value is the new name
        columns_to_rename = {
            'start_zone_name': 'start_zone',
            'end_zone_name': 'end_zone',
            'start_departure_time': 'start_time',
            'end_departure_time': 'end_time',
        }

        # Renaming columns
        for original_name, new_name in columns_to_rename.items():
            d[new_name] = d[original_name]
            del d[original_name]

        d['num_zones'] = group.zone_name.nunique()
        d['num_zones_missing'] = group.zone_name.isnull().sum()
        dist = geometry_by_stop[d['start_stop_id']].distance(
            geometry_by_stop[d['end_stop_id']])
        d['is_loop'] = int(dist < 400)
        d['duration'] = (d['end_departure_time'] - d['start_departure_time']) / 3600

        d['all_stop_latlon'] = ';'.join(str(x) + ',' + str(y) for x, y in
                                        zip(group['stop_lat'].tolist(), group['stop_lon'].tolist()))

        d['all_stop_code'] = ';'.join(group['stop_code'].tolist())
        d['all_stop_id'] = ';'.join(group['stop_id'].tolist())
        d['all_stop_desc_city'] = ';'.join(group['stop_desc_city'].tolist())

        return pd.Series(d)

    return trip_stats_aggregation


def generate_route_stats_aggregation(headway_start_time, headway_end_time):

    headway_start = gtfstk.helpers.timestr_to_seconds(headway_start_time)
    headway_end = gtfstk.helpers.timestr_to_seconds(headway_end_time)

    def route_stats_aggregation(group):
        d = OrderedDict()
        keys = [
            'route_short_name', 'route_long_name', 'route_mkt', 'route_direction',
            'route_alternative', 'agency_id', 'agency_name', 'route_type', 'start_stop_id',
            'end_stop_id', 'start_stop_name', 'end_stop_name', 'start_stop_desc', 'end_stop_desc',
            'start_stop_lat', 'start_stop_lon', 'end_stop_lat', 'end_stop_lon', 'start_stop_desc_city',
            'end_stop_desc_city', 'num_stops', 'start_zone_name', 'end_zone_name', 'num_zones',
            'num_zones_missing', 'all_stop_latlon', 'all_stop_code', 'all_stop_id',
            'all_stop_desc_city'
        ]
        for key in keys:
            d[key] = group[key].iat[0]


        d['num_trips'] = group.shape[0]
        d['num_trip_starts'] = group['start_departure_time'].count()
        d['num_trip_ends'] = group.loc[
            group['end_departure_time'] < 24 * 3600, 'end_departure_time'].count()
        d['is_loop'] = int(group['is_loop'].any())
        d['is_bidirectional'] = int(group['direction_id'].unique().size > 1)
        d['start_departure_time'] = group['start_departure_time'].min()
        d['end_departure_time'] = group['end_departure_time'].max()

        # Compute headway stats
        headways = np.array([])
        for direction in [0, 1]:
            stimes = group[group['direction_id'] == direction][
                'start_departure_time'].values
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
        active_trips = get_active_trips_df(group[['start_departure_time', 'end_departure_time']])
        times, counts = active_trips.index.values, active_trips.values
        start, end = gtfstk.helpers.get_peak_indices(times, counts)
        d['peak_num_trips'] = counts[start]
        d['peak_start_time'] = times[start]
        d['peak_end_time'] = times[end]

        d['service_distance'] = group['distance'].sum()
        d['service_duration'] = group['duration'].sum()


        d['all_start_time'] = ';'.join([gtfstk.helpers.timestr_to_seconds(x, inverse=True)
                                        for x in group['start_departure_time'].tolist()])
        d['all_trip_id'] = ';'.join(group['trip_id'].tolist())
        return pd.Series(d)

    return route_stats_aggregation


def get_active_trips_df(trip_times):
    """
    Count the number of trips in ``trip_times`` that are active
    at any given time.

    Parameters
    ----------
    trip_times : DataFrame
        Contains columns

        - start_departure_time: start time of the trip in seconds past midnight
        - end_departure_time: end time of the trip in seconds past midnight

    Returns
    -------
    Series
        index is times from midnight when trips start and end, values are number of active trips for that time

    """
    active_trips = pd.concat([pd.Series(1, trip_times.start_departure_time),  # departed add 1
                              pd.Series(-1, trip_times.end_departure_time)  # arrived subtract 1
                              ]).groupby(level=0, sort=True).sum().cumsum().ffill()
    return active_trips

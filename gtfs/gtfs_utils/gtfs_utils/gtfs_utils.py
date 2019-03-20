import pandas as pd
import partridge as ptg
import zipfile
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


def get_cluster_to_line_df(path):
    cols = ['agency_name', 'route_id', 'route_short_name',
            'cluster_name', 'from_date', 'to_date', 'cluster_id',
            'route_type', 'route_type_desc', 'cluster_sub_desc', 'EXTRA']
    ctl = (pd.read_csv(path, encoding='utf-8',
                       skiprows=[0], header=None, names=cols)
           .drop(columns=['EXTRA']))
    return ctl


def get_train_office_line_id_df(path):
    cols = ['office_line_id', 'operator_line_id', 'direction', 'line_alternative', 'train_office_line_id',
            'line_detail_record_id', 'from_date', 'to_date', 'trip_id', 'EXTRA']
    tolid = (pd.read_csv(path, encoding='windows-1255',
                         skiprows=[0], header=None, names=cols)
             .drop(columns=['EXTRA']))
    return tolid


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


def get_tidy_feed_df(feed, extra_merges):
    # merge selected fields from selected GTFS files in a stated order
    # perform extra merges with a list of other dataframes `extra_merges`
    # make categorical fields into pd.Categorical
    # perform transforms (e.g. turn times into timedelta)

    # first field is the id field, and the one we will merge on
    fields = {
        'stop_times': ['trip_id', 'departure_time', 'arrival_time', 'stop_id', 'stop_sequence'],
        'stops': ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'stop_code'],
        'trips': ['trip_id', 'route_id', 'direction_id'],
        'routes': ['route_id', 'route_short_name', 'route_long_name', 'agency_id'],
        'agency': ['agency_id', 'agency_name'],
    }

    categoricals = ['route_id', 'zone_name', 'route_id', 'agency_id', 'agency_name', 'route_short_name', 'direction_id']

    transforms = {'arrival_time': (pd.to_timedelta, {'unit': 's'}),
                  'departure_time': (pd.to_timedelta, {'unit': 's'})}

    accum_df = None

    for i, f in enumerate(fields):
        df = feed.__getattribute__(f)[fields[f]]

        if i == 0:
            accum_df = df
        else:
            accum_df = accum_df.merge(df, how='left', on=fields[f][0])

    if accum_df is None:
        return None

    for em in extra_merges:
        accum_df = accum_df.merge(em, how='left')

    for c in categoricals:
        if c in accum_df.columns:
            accum_df[c] = pd.Categorical(accum_df[c])

    for trans_field in transforms:
        func, kwargs = transforms[trans_field]
        accum_df[trans_field] = accum_df[trans_field].apply(func, **kwargs)

    return accum_df

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
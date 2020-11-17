# Parse raw siri files for local data analysis
import gzip
import json
import re
from json import JSONDecodeError
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from collections.abc import Iterable


# ========================= 2.8

SIRI28_TYPES = {
    '-version': np.float32,
    'ResponseTimestamp': 'dt',
    'Status': bool,
    'RecordedAtTime': 'dt',
    'ItemIdentifier': int,
    'MonitoringRef': int,
    'LineRef': int,
    'DirectionRef': int,
    'DataFrameRef': 'date',
    'DatedVehicleJourneyRef': int,
    'PublishedLineName': str,
    'OperatorRef': int,
    'DestinationRef': int,
    'OriginAimedDepartureTime': 'dt',
    'Bearing': int,
    'Velocity': int,
    'VehicleRef': int,
    'StopPointRef': int,
    'Order': int,
    'AimedArrivalTime': 'dt',
    'ExpectedArrivalTime': 'dt',
    'DistanceFromStop': int,
    'Longitude': np.float32,
    'Latitude': np.float32,
    'ArrivalStatus': str,
    'ArrivalPlatformName': int,
}

SIRI28_CATEGORICALS = ['arrival_status', '_version', 'operator_ref']

# UNSIGNED = ['item_identifier', 'direction_ref', 'line_ref', 'item_identifier',
#      'monitoring_ref',
#             'dated_vehicle_journey_ref', 'operator_ref', 'destination_ref', 'bearing', 'velocity',
#             'vehicle_ref', 'stop_point_ref', 'order', 'distance_from_stop']
# DOWNCAST = ['longitude', 'latitude', 'arrival_platform_name', '_version']
# def castings(df):
#     for c in unsigned:
#         df[unsigned] = df[unsigned].apply(pd.to_numeric, downcast='unsigned')
#
#         df[downcast] = df[downcast].apply(pd.to_numeric, downcast='float')

# def get_snap_df(daily_path):
#     dfs = []
#     for folder in os.scandir(daily_path):
#         if not os.path.isdir(folder):
#             continue
#         fold_dfs = []
#         for file in sorted(os.scandir(folder), key=lambda e: e.name):
#             if 'normal' in file.name and file.name.endswith('.json.gz'):
#                 try:
#                     fold_dfs.append(read_siri_snap_normal(file.path))
#                 except Exception as e:
#                     print(file.path, e)
#
#         if fold_dfs:
#             dfs.append(pd.concat(fold_dfs))
#         else:
#             print('No files in', folder.name)
#
#     df = pd.concat(dfs)
#     castings(df)
#     return df

def camel_to_snake(name):
    """
    Converts a string that is camelCase into snake_case
    """
    name = name.replace('-', '_')
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def read_siri28_file(path):
    """
    Read one siri 2.8 json file and parse to df
    """
    # read json
    if path.name.endswith('.gz'):
        with gzip.GzipFile(path, 'r') as fin:
            data = json.loads(fin.read().decode('utf-8'))
    else:
        with open(path, 'r') as fin:
            data = json.loads(fin.read())


    # flatten to df
    records = data['Siri']['ServiceDelivery']['StopMonitoringDelivery']
    df = json_normalize(
        data=records,
        record_path=['MonitoredStopVisit'],
        # meta=['ResponseTimestamp'],
        meta=['-version', 'ResponseTimestamp', 'Status'],
    )

    # remove prefixes from column names for simplicity
    df.columns = [col.split('.')[-1] for col in df.columns]

    # set types (default is 'object' for all fields
    cur_int_cols = [f for f, v in SIRI28_TYPES.items()
                    if v is int and f in df.columns]
    df[cur_int_cols] = df[cur_int_cols].fillna(-1)  # [Adi] I think this is
    # because pd<1.0 does not accept null for ints. This should be allowed in
    # pd 1.0
    df = df.astype({f: v for f, v in SIRI28_TYPES.items() if type(v) is not
                    str and f in df.columns})
    dt_cols = [f for f, v in SIRI28_TYPES.items()
               if v == 'dt' and f in df.columns]
    for f in dt_cols:
        df[f] = pd.to_datetime(df[f])

    # column names camelCase to snake_case
    snake_cols = {k: camel_to_snake(k) for k in SIRI28_TYPES}
    df = df.rename(columns=snake_cols)

    # TODO reduce size with castings / categoricals

    return df


def read_siri28_files(siri_input, max_files=None, suf='.json.gz'):
    """
    Read multiple siri 2.8 json files, and concat them to one df
    :param siri_input: path to directory with files, or list of files paths.
    """
    if isinstance(siri_input, str):
        files = Path(siri_input).rglob('*' + suf)  # recursive search
        if not files:
            raise ValueError("No {} files in dir".format(suf), siri_input)
    elif isinstance(siri_input, Iterable):
        files = siri_input
    else:
        raise ValueError("siri_input must be a path to directory or iterable "
                         "of siri files paths")

    if max_files is not None:
        n = max_files

    # read with errors resiliency:
    dfs = []
    for f in files:
        try:
            df = read_siri28_file(f)
            dfs.append(df)
        except JSONDecodeError as e:
            print(f, e)

        if max_files is not None:
            n -= 1
            if n == 0:
                break

    df = pd.concat(dfs, sort=False, ignore_index=True)

    df[SIRI28_CATEGORICALS] = df[SIRI28_CATEGORICALS].astype('category')

    return df


# ========================= 2.7

SIRI_27_TYPES = {
    # 'timestamp': pd.datetime,
    'agency_id': int,
    'route_id': int,
    'route_short_name': str,
    'service_id': int,
    'planned_start_date': str,
    'planned_start_time': str,
    'bus_id': int,
    'predicted_end_date': str,
    'predicted_end_time': str,
    'date_recorded': str,
    'time_recorded': str,
    'lat': np.float32,
    'lon': np.float32,
    'stop_point_ref': int,
    'date': str,
    'num_duplicates': int,
}


SIRI_27_DT = {
    'planned_start_dt': [5, 6],
    'predicted_end_dt': [8, 9],
    'dt_recorded': [10, 11],
}


def read_siri27_file(path):
    df = pd.read_csv(path, dtype=SIRI_27_TYPES, parse_dates=SIRI_27_DT)
    df['timestamp'] = pd.to_datetime(df.timestamp)
    return df


def read_siri27_files(siri_input, max_files=None):
    if isinstance(siri_input, str):
        files = Path(siri_input).rglob('*.csv.gz')  # recursive search
        if not files:
            raise ValueError("No .csv.gz files in dir", siri_input)
    elif isinstance(siri_input, Iterable):
        files = siri_input
    else:
        raise ValueError("siri_input must be a path to directory or iterable "
                         "of siri files paths")

    if max_files is not None:
        n = max_files
    else:
        n = 0

    # read with errors resiliency:
    dfs = []
    for f in files:
        # try:
        df = read_siri27_file(f)
        dfs.append(df)
        # except JSONDecodeError as e:
        #     print(f, e)

        if max_files is not None:
            n -= 1
            if n == 0:
                break

    df = pd.concat(dfs, sort=False, ignore_index=True)

    # df[SIRI28_CATEGORICALS] = df[SIRI28_CATEGORICALS].astype('category')

    return df



# This module creates a tabular data from SIRI bus real-time GPS data
# downloaded from MoT using SIRI-retreiver

import datetime
from glob import glob
import numpy as np
import os
import pandas as pd
import re
import sys


def timestr_to_seconds(x, *, only_mins=False):
    try:
        hms = x.str.split(':', expand=True)
        if not only_mins:
            result = hms.iloc[:, 0].astype(int) * 3600 + hms.iloc[:, 1].astype(int) * 60 + \
                     hms.iloc[:, 2].astype(int)
        else:
            result = hms.iloc[:, 0].astype(int) * 3600 + hms.iloc[:, 1].astype(int) * 60
    except:
        result = np.nan

    return result


# TODO - must test the function after our changes
def create_trip_df_v2(path, add_date=True):
    """ Process log file with raw siri data coming from SIRI retreiver service to make
    it ready for being dumped into the Open Bus splunk database.

    Processing include splitting columns and converting columns types.

    This function determines the format of the real-time bus data we store,
    and therefore this documentation is an important building block of Open Bus data.

    This function is heavily based on the format of the log file, and therefore should be
    adjusted on any change being done to it in the SIRI retreiver code.

    This function started being used online on June 2019, when the SIRI retreiver was updated to
    retrieve more data fields such as "planned_start_date".
    ## explain explicitly the changes from v1.

    :param path: path to csv file which is the log output of SIRI retreiver
                    ##mention specific function#
    :param add_date: bool, for now, used only for backward compatibility to v1, which
    had to "planned start date" field. After we will rerun the adjustments of v2 on v1 processed
    data, this field can be removed. The user should change the default value.
    #TODO edit

    TODO - add details about the Jenkins service that runs this script automatically and saves
            at S3.

    :return: pandas DataFrame with columns as described below

    Real time bus data table has the following columns:

    ## TODO - when finished, order the columns alphabetically
    ## TODO - provide link to the GTFS stats docs, and explain that many columns can be
              joined to the data there to extract more information.

    TODO - add reference to the relevant original GTFS field name and the original siri name.

    - ``timestamp`` - Time of receiving the record, determined by the time zone configured for
                      the machine that the siri_retreiver runs on, which is aimed to be configured
                      to Israel time. We don't know now about the clock daylight saving times.
                      Should be used only relatively
                       to other timestamps,
    TODO - how to describe formally the time zone, and include explanation of summer/winter clock.
    TODO - add exact format of the timestamp.
    - ``agency_id`` - Identifies a transit brand that operates the service.
    TODO provide more details about the possible ids and the way to cross them with agency names
    - ``route_id`` - Identifies a route. In our data, route mostly represents a specific path that
                     the bus travels. Multiple route ids with a single `route_short_name` represent
                     multiple alternatives for the same line ("חלופות") that are mostly differ by
                     a small number of stops.
    - ``route_short_name`` - A short, abstract identifier like that riders use to identify a route,
                             but which doesn't give any indication of what places the route serves.
                             There could be multiple route_id values for the same
                             `route_short_name`, representing either a few close alternatives of
                             the same route, or absolutely different routes - mostly in different
                             areas and/or operated by different agencies.
    - ``service_id`` -



    "", "", "",
             "planned_start_date", "planned_start_time", "bus_id",
             "predicted_end_date", "predicted_end_time",
             "date_recorded", "time_recorded", "lat", "lon",
             "data_frame_ref", "stop_point_ref", "vehicle_at_stop",
             "log_version", "date"



    """
    header = ["timestamp", "desc", "agency_id",
              "route_id", "route_short_name", "service_id",
              "planned_start_time", "bus_id", "predicted_end_time",
              "time_recorded", "lat", "lon",
              "data_frame_ref", "stop_point_ref", "vehicle_at_stop",
              "log_version"]
    df = pd.read_csv(path, header=None, error_bad_lines=False)
    df.columns = header # TODO - why not directly mentioning it within the read_csv command?

    df = (df.assign(agency_id=lambda x: x.agency_id.astype(int))
          .assign(service_id=lambda x: x.service_id.astype(int))
          .assign(route_id=lambda x: x.route_id.astype(int))
          .assign(lat=lambda x: x.lat.astype(float))
          .assign(lon=lambda x: x.lon.astype(float)))

    df[['date_recorded', 'time_recorded']] = df.time_recorded.str.split('T', expand=True)
    df[['predicted_end_date', 'predicted_end_time']] = df.predicted_end_time.str.split('T', expand=True)
    df[['planned_start_date', 'planned_start_time']] = df.planned_start_time.str.split('T', expand=True)

    output_cols = ["timestamp", "agency_id",
             "route_id", "route_short_name", "service_id",
             "planned_start_date", "planned_start_time", "bus_id",
             "predicted_end_date", "predicted_end_time",
             "date_recorded", "time_recorded", "lat", "lon",
             "data_frame_ref", "stop_point_ref", "vehicle_at_stop",
             "log_version"]

    if add_date:
        df = (df.assign(date=lambda x: x.planned_start_date))
        output_cols += ["date"]

    df = df[output_cols]
    return df


def create_trip_df(path, drop=['timestamp', 'desc'],
                   convert_timestr_to_seconds=True, add_date=True,
                   add_trailing_zeros=True):
    """
    Was relevant until June 2019
    :param path:
    :param drop:
    :param convert_timestr_to_seconds:
    :param add_date:
    :param add_trailing_zeros:
    :return:
    """
    header = ["timestamp", "desc", "agency_id",
              "route_id", "route_short_name", "service_id",
              "planned_start_time", "bus_id", "predicted_end_time",
              "time_recorded", "lat", "lon"]
    date = datetime.datetime.strptime(re.findall('siri_rt_data\\.([^\\.]+)\\.\\d+\\.log', path)[0], '%Y-%m-%d')
    df = pd.read_csv(path, header=None, error_bad_lines=False)
    df.columns = header
    if drop is not None:
        df = df.drop(drop, axis=1)
    df = (df.assign(agency_id=lambda x: x.agency_id.astype(int))
          .assign(service_id=lambda x: x.service_id.astype(int))
          .assign(route_id=lambda x: x.route_id.astype(int))
          .assign(lat=lambda x: x.lat.astype(float))
          .assign(lon=lambda x: x.lon.astype(float)))
    if convert_timestr_to_seconds:
        df = (df.assign(planned_start_time=lambda x: timestr_to_seconds(x.planned_start_time, only_mins=True))
              .assign(predicted_end_time=lambda x: timestr_to_seconds(x.predicted_end_time, only_mins=True))
              .assign(time_recorded=lambda x: timestr_to_seconds(x.time_recorded)))
    if add_date:
        df = (df.assign(date=date))
    if add_trailing_zeros:
        df = (df
              .assign(planned_start_time=lambda x: x.planned_start_time + ':00')
              .assign(predicted_end_time=lambda x: x.predicted_end_time + ':00'))

    return df


def main(FOLDER, out_folder):
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    for file in glob(FOLDER + '/*'):
        base = '.'.join(os.path.basename(file).split('.')[:-2])
        version = re.match("siri_rt_data_([^\.]*)\.", os.path.basename(file)).groups()[0]
        out_path = os.path.join(out_folder, base + '.csv.gz')
        if not os.path.exists(out_path):
            # out_path = os.path.join(out_folder, base+'_FIXED.csv.gz')
            print(file)
            try:
                if version == '':
                    df = create_trip_df(file, drop=['desc'], convert_timestr_to_seconds=False)
                elif version == 'v2':
                    df = create_trip_df_v2(file)
            except Exception as e:
                print(str(e))
            # df.to_parquet(bn + '.parq')
            # os.remove(file)
            df.to_csv(out_path, compression='gzip', index=False)


if __name__ == '__main__':
    FOLDER, out_folder = sys.argv[1], sys.argv[2]
    main(FOLDER, out_folder)

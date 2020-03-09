from glob import glob
import os
import pandas as pd
import datetime
import re
from os.path import join
import sys

def timestr_to_seconds(x, *, only_mins=False):
    try:
        hms = x.str.split(':', expand=True)
        if not only_mins:
            result = hms.iloc[:,0].astype(int) * 3600 + hms.iloc[:,1].astype(int) * 60 + hms.iloc[:,2].astype(int)
        else:
            result = hms.iloc[:,0].astype(int) * 3600 + hms.iloc[:,1].astype(int) * 60
    except:
        result = np.nan

    return result

def create_trip_df(path, drop=['timestamp', 'desc'],
                   convert_timestr_to_seconds=True, add_date=True,
                   add_trailing_zeros=True):
    header = ["timestamp", "desc", "agency_id",
              "route_id", "route_short_name", "service_id",
              "planned_start_time", "bus_id", "predicted_end_time",
              "time_recorded", "lat", "lon"]
    date = datetime.datetime.strptime(re.findall('siri_rt_data\\.([^\\.]+)\\.\\d+\\.log', path)[0], '%Y-%m-%d')
    df = pd.read_csv(path, header=None, error_bad_lines=False)
    df.columns = header
    if drop is not None:
        df = df.drop(drop, axis=1)
    df = (df.assign(agency_id = lambda x: x.agency_id.astype(int))
              .assign(service_id = lambda x: x.service_id.astype(int))
              .assign(route_id = lambda x: x.route_id.astype(int))
              .assign(lat = lambda x: x.lat.astype(float))
              .assign(lon = lambda x: x.lon.astype(float)))
    if convert_timestr_to_seconds:
        df = (df.assign(planned_start_time = lambda x: timestr_to_seconds(x.planned_start_time, only_mins=True))
                .assign(predicted_end_time = lambda x: timestr_to_seconds(x.predicted_end_time, only_mins=True))
                .assign(time_recorded = lambda x: timestr_to_seconds(x.time_recorded)))
    if add_date:
        df = (df.assign(date = date))
    if add_trailing_zeros:
        df = (df
                .assign(planned_start_time = lambda x: x.planned_start_time+':00')
                .assign(predicted_end_time = lambda x: x.predicted_end_time+':00'))

    return df

def create_trip_df_v2(path, drop=['desc'],
                       add_date=True,
                       remove_zero_latlons=False,
                       drop_duplicates=True):
    header = ["timestamp", "desc", "agency_id",
              "route_id", "route_short_name", "service_id",
              "planned_start_time", "bus_id", "predicted_end_time",
              "time_recorded", "lat", "lon",
              "data_frame_ref", "stop_point_ref", "vehicle_at_stop",
              "log_version"]
    df = pd.read_csv(path, header=None, error_bad_lines=False)
    df.columns = header
    if drop is not None:
        df = df.drop(drop, axis=1)
    df = (df.assign(agency_id = lambda x: x.agency_id.astype(int))
              .assign(service_id = lambda x: x.service_id.astype(int))
              .assign(route_id = lambda x: x.route_id.astype(int))
              .assign(lat = lambda x: x.lat.astype(float))
              .assign(lon = lambda x: x.lon.astype(float)))
    
    if remove_zero_latlons:
        df = df[(df.lat!=0) & (df.lon!=0)]
        
    if drop_duplicates:
        new_df = df.groupby(["agency_id",
              "route_id", "route_short_name", "service_id",
              "planned_start_time", "bus_id", "predicted_end_time",
              "time_recorded", "lat", "lon",
              "stop_point_ref",], sort=False).first()
        new_df['num_duplicates'] = df.groupby(["agency_id",
              "route_id", "route_short_name", "service_id",
              "planned_start_time", "bus_id", "predicted_end_time",
              "time_recorded", "lat", "lon",
              "stop_point_ref",], sort=False).size()
        df = new_df.reset_index()
        
        
    df[['date_recorded', 'time_recorded']] = df.time_recorded.str.split('T', expand=True)
    df[['predicted_end_date', 'predicted_end_time']] = df.predicted_end_time.str.split('T', expand=True)
    df[['planned_start_date', 'planned_start_time']] = df.planned_start_time.str.split('T', expand=True)

    # removed  'data_frame_ref' because it is useless (always the current date)
    # removed 'vehicle_at_stop' because it is useless (always 2)
    # removed 'log_version' because you can get it from the file name 
    final_cols = ["timestamp", "agency_id",
                  "route_id", "route_short_name", "service_id",
                  "planned_start_date", "planned_start_time", "bus_id", "predicted_end_date", "predicted_end_time",
                  "date_recorded", "time_recorded", "lat", "lon",
                  "stop_point_ref"]
    
    if add_date:
        df = (df.assign(date = lambda x: x.planned_start_date))
        final_cols.append('date')
        
    if drop_duplicates:
        final_cols.append('num_duplicates')
        
    df = df[final_cols]
    return df


def main(FOLDER,out_folder):
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    for file in glob(FOLDER+'/*'):
        base = '.'.join(os.path.basename(file).split('.')[:-2])
        version = re.match("siri_rt_data_([^\.]*)\.", os.path.basename(file)).groups()[0]
        out_path = os.path.join(out_folder, base+'.csv.gz')
        if not os.path.exists(out_path):
            #out_path = os.path.join(out_folder, base+'_FIXED.csv.gz')
            print(file)
            try:
                if version=='':
                    df = create_trip_df(file, drop=['desc'], convert_timestr_to_seconds=False)
                elif version=='v2':
                    df = create_trip_df_v2(file)
            except Exception as e:
                print(str(e))
            #df.to_parquet(bn + '.parq')
            #os.remove(file)
            df.to_csv(out_path, compression='gzip', index=False)

if __name__ == '__main__':
    FOLDER,out_folder = sys.argv[1],sys.argv[2]
    main(FOLDER,out_folder)

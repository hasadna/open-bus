from glob import glob
import os
import pandas as pd
import datetime
import re
from os.path import join

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
    
FOLDER = '<SIRI_LOGS_FOLDER>'
out_folder = '<SPLUNK_SIRI_CSV_INPUTS_FOLDER>'
if not os.path.exists(out_folder):
    os.mkdir(out_folder)

for file in glob(FOLDER+'/*2019*.log.gz'):
    base = '.'.join(os.path.basename(file).split('.')[:-2])
    out_path = os.path.join(out_folder, base+'.csv.gz')
    if not os.path.exists(out_path):
        #out_path = os.path.join(out_folder, base+'_FIXED.csv.gz')
        print(file)
        try:
            df = create_trip_df(file, drop=['desc'], convert_timestr_to_seconds=False)
        except Exception as e:
            print(str(e))
        #df.to_parquet(bn + '.parq')
        #os.remove(file)
        df.to_csv(out_path, compression='gzip', index=False)

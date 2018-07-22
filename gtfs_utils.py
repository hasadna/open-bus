import pandas as pd
import partridge as ptg
from ftplib import FTP
import datetime
import re
import zipfile
import os

MOT_FTP = 'gtfs.mot.gov.il'
GTFS_FILE_NAME = 'israel-public-transportation.zip'
LOCAL_ZIP_PATH = 'data/sample/gtfs.zip' 
TEMP_LOCAL_PATH = 'data/sample/gtfs_temp.zip'
TARIFF_FILE_NAME = 'Tariff.zip'
TARIFF_TXT_NAME = 'Tariff.txt'
TARIFF_TO_REFORM_ZONE = 'StationToReformZone.txt'

RE_FTP_LINE = re.compile(
    r'(?P<date>\d+-\d+-\d+\s+\d+:\d+[APM]{2})\s+(?P<size><DIR>|[0-9]+)\s+(?P<file_name>.*)')
    
def ftp_connect():
    conn = FTP(MOT_FTP)
    conn.login()
    return conn

def get_ftp_dir(conn = None):
    close = False

    if conn is None:
        conn = ftp_connect()
        close = True

    ftp_dir = []
    conn.retrlines('LIST', lambda x: ftp_dir.append(x)) 

    return ftp_dir

def get_uptodateness(ftp_dir, file_name = GTFS_FILE_NAME, local_path = LOCAL_ZIP_PATH):
    # returns how many days behind the local file is compared to the ftp file
    # based on file modified dates

    f = [re.findall(RE_FTP_LINE, line) for line in ftp_dir]
    f_dates = {t[0][2]: datetime.datetime.strptime(t[0][0], "%m-%d-%y  %H:%M%p") for t in f}

    ftp_date = f_dates[file_name]

    our_date = datetime.datetime.fromtimestamp(os.path.getmtime(local_path))
    return  (ftp_date - our_date).days

def get_ftp_file(conn=None, file_name = GTFS_FILE_NAME, local_path = LOCAL_ZIP_PATH, force=False):
    close = False

    if conn is None:
        conn = ftp_connect()
        close = True

    if not force and os.path.exists(local_path):
        raise FileExistsError(f'Local file \'{local_path}\' already exists, consider changing name for archiving purposes, or use the `force` flag') 

    print(f'Downloading {file_name}...')

    with open(local_path, 'wb') as fh:
        conn.retrbinary('RETR %s' % (file_name), fh.write)
    print('Done.')
    
    if close: conn.close()
    return True

def get_zones_df(local_tariff_zip_path):
    # not a true csv, so we need to jiggle it a bit, hence the 'EXTRA' field
    tariff_cols = ['ShareCode','ShareCodeDesc','ZoneCodes','Daily','Weekly','Monthly','FromDate','ToDate', 'EXTRA']
    reform_cols = ['StationId', 'ReformZoneCode','FromDate','ToDate', 'EXTRA']
    with zipfile.ZipFile(local_tariff_zip_path) as zf:
        tariff_df = (pd.read_csv(zf.open(TARIFF_TXT_NAME), header=None, skiprows=[0], names = tariff_cols)
                    .drop(columns = ['EXTRA']))
        reform_df = (pd.read_csv(zf.open(TARIFF_TO_REFORM_ZONE), header=None, skiprows=[0], names = reform_cols)
                     .drop(columns = ['EXTRA']))

    # remove ShareCodes which contain multiple zones  e.g. גוש דן מורחב
    tariff_df = (tariff_df[~ tariff_df.ZoneCodes.str.contains(';')]
                 .rename(columns = {'ShareCodeDesc': 'zone_name',
                                   'ZoneCodes': 'zone_id'}))
    rs = reform_df[['StationId', 'ReformZoneCode']].drop_duplicates().applymap(str).set_index('StationId').iloc[:,0]

    ts = (tariff_df[['zone_id', 'zone_name']].drop_duplicates().set_index('zone_id').iloc[:,0])
    zones = rs.map(ts).reset_index().rename(columns={'StationId': 'stop_code', 'ReformZoneCode':'zone_name'})
    return zones

def get_partridge_feed_by_date(zip_path, date):
    service_ids_by_date = ptg.read_service_ids_by_date(zip_path)#, encoding='utf-8')
    service_ids = service_ids_by_date[date]

    feed = ptg.feed(zip_path, view={
        'trips.txt': {
            'service_id': service_ids,
            },
        },
        #encoding='utf-8' # CUSTOM VERSION, NOT YET PUSHED
    )
    return feed
    
def get_tidy_feed_df(feed, extra_merges, extra_fields=None):
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
           
        if i==0:
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

def write_feed_dangerously(feed, outpath):
    return ptg.writers.write_feed_dangerously(feed, outpath)


############
# OBSOLETE #
############

def extract_tariff_df(local_zip_path, tariff_txt_name = TARIFF_TXT_NAME):
    cols = ['ShareCode','ShareCodeDesc','ZoneCodes','Daily','Weekly','Monthly','FromDate','ToDate', 'EXTRA']
    with zipfile.ZipFile(local_zip_path) as zf:
        tariff_df = (pd.read_csv(zf.open(tariff_txt_name), header=None, skiprows=[0], names = cols)
        .drop(columns = ['EXTRA']))
    # remove ShareCodes which contain multiple zones  e.g. גוש דן מורחב
    tariff_df = (tariff_df[~ tariff_df.ZoneCodes.str.contains(';')]
                 .rename(columns = {'ShareCodeDesc': 'zone_name',
                                   'ZoneCodes': 'zone_id'}))
    return tariff_df


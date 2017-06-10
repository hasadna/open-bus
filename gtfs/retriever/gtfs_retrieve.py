import os
import shutil

import gtfs_utils

MOT_FTP = 'gtfs.mot.gov.il'
FILE_NAME = 'israel-public-transportation.zip'

def download_gtfs_file(force=False):
    """ download gtfs zip file from mot, and put it in DATA_DIR in its own subfolder """
    GTFS_DATA_DIR = os.path.join('gtfs_data')
    if not os.path.exists(GTFS_DATA_DIR):
        os.makedirs(GTFS_DATA_DIR)
    
    time_suffix = gtfs_utils.get_utc_time_underscored()
    tmp_file = '/tmp/%s_gtfs_tmp.zip' % (time_suffix)
    
    print('Downloading GTFS to tmp file...')
    gtfs_utils.ftp_get_file(MOT_FTP, FILE_NAME, tmp_file)
    
    if not force:
        last_dir = gtfs_utils.find_lastest_in_dir(GTFS_DATA_DIR)
        if last_dir:
            last_file = os.path.join(last_dir, FILE_NAME)
            try:
                tmp_md5 = gtfs_utils.md5_for_file(tmp_file)
                last_md5 = gtfs_utils.md5_for_file(last_file)
            except Exception as e:
                print(e)
                tmp_md5 = 'none'
                last_md5 = 'error_in_md5'
            if last_md5 == tmp_md5:
                print('Checksums are identical - removing tmp file...')
                os.remove(tmp_file)
                return None
    
    print('No file exists yet, checksum for latest is different or force enabled -> copying...')
    local_dir = os.path.join(GTFS_DATA_DIR, time_suffix)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    local_file = os.path.join(local_dir, FILE_NAME)
    shutil.move(tmp_file, local_file)
    
    print('GTFS file retrieved to ', local_dir)
    return local_dir

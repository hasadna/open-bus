import os
import datetime
import re
from ftplib import FTP
from .constants import *


RE_FTP_LINE = re.compile(
    r'(?P<date>\d+-\d+-\d+\s+\d+:\d+[APM]{2})\s+(?P<size><DIR>|[0-9]+)\s+(?P<file_name>.*)')


def ftp_connect():
    conn = FTP(MOT_FTP)
    conn.login()
    return conn


def get_ftp_dir(conn=None):
    close = False

    if conn is None:
        conn = ftp_connect()
        close = True

    ftp_dir = []
    conn.retrlines('LIST', lambda x: ftp_dir.append(x))

    if close:
        conn.close()

    return ftp_dir


def get_uptodateness(ftp_dir, file_name=GTFS_FILE_NAME, local_path=LOCAL_ZIP_PATH):
    # returns how many days behind the local file is compared to the ftp file
    # based on file modified dates

    f = [re.findall(RE_FTP_LINE, line) for line in ftp_dir]
    f_dates = {t[0][2]: datetime.datetime.strptime(t[0][0], "%m-%d-%y  %H:%M%p") for t in f}

    ftp_date = f_dates[file_name]

    our_date = datetime.datetime.fromtimestamp(os.path.getmtime(local_path))
    return (ftp_date - our_date).days


def get_ftp_file(conn=None, file_name=GTFS_FILE_NAME, local_path=LOCAL_ZIP_PATH, force=False):
    close = False

    if conn is None:
        conn = ftp_connect()
        close = True

    if not force and os.path.exists(local_path):
        raise FileExistsError(
            f'Local file \'{local_path}\' already exists, consider changing name for archiving purposes, or use the \
            `force` flag')

    print(f'Downloading {file_name}...')

    with open(local_path, 'wb') as fh:
        conn.retrbinary('RETR %s' % file_name, fh.write)
    print('Done.')

    if close:
        conn.close()

    return True


import os
import datetime
import re
from ftplib import FTP
from os.path import dirname

from gtfs.gtfs_utils.gtfs_utils.environment import get_free_space_bytes
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


def validate_enough_disk_space(conn=None, file_names=(GTFS_FILE_NAME,), local_path=LOCAL_ZIP_PATH):
    close = False

    if conn is None:
        conn = ftp_connect()
        close = True

    # confirm enough disk space
    free_space = get_free_space_bytes(dirname(local_path))
    ftp_files_size = sum([conn.size(file_name) for file_name in file_names])
    if not free_space > ftp_files_size:
        raise IOError(
            f'There is no enough free disk space for the files {file_names!r} to be saved in {local_path!r}.\n'
            f'free space - {free_space / 1024 / 1024}MB and the file size is - {ftp_files_size / 1024 / 1024}MB'
        )

    if close:
        conn.close()


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


import ftplib
import os
from ftplib import FTP
import re
import hashlib
import logging.config
import datetime

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger("default")


def ftp_get_file(local_path, host, remote_file_name):
    """ get file remote_file_name from FTP host and copy it into local_path """
    logger.info("Starting to download '%s' from host '%s' => '%s'" % (remote_file_name, host, local_path))
    try:
        ftp = FTP(host)
        ftp.login()
        fh = open(local_path, 'wb')
        ftp.retrbinary('RETR %s' % remote_file_name, fh.write)
        fh.close()
        ftp.quit()
        logger.info("Finished downloading '%s' from host '%s' => '%s'" % (remote_file_name, host, local_path))

    except ftplib.all_errors as e:
        error_code_string = str(e).split(None, 1)[0]
        logger.error("Error downloading '%s' from host '%s' => '%s': %s" % (remote_file_name, host, local_path,
                                                                            error_code_string))


def get_uptodateness(local_timestamp, host, remote_file_name):
    """" returns true if remote file timestamp is newer than local_timestamp """
    conn = FTP(host)
    conn.login()
    ftp_dir_array = []
    conn.retrlines('LIST', lambda x: ftp_dir_array.append(x))
    conn.quit()

    # Extract the date from the 'dir' result and put into a dict
    re_ftp_line = re.compile(
        r'(?P<date>\d+-\d+-\d+\s+\d+:\d+[APM]{2})\s+(?P<size><DIR>|[0-9]+)\s+(?P<remote_file_name>.*)')
    re_on_ftp_dir_result = [re.findall(re_ftp_line, line) for line in ftp_dir_array]
    ftp_dir_dates = {t[0][2]: datetime.datetime.strptime(t[0][0], "%m-%d-%y  %H:%M%p") for t in re_on_ftp_dir_result}

    remote_file_date = ftp_dir_dates[remote_file_name]
    local_file_date = datetime.datetime.fromtimestamp(local_timestamp)

    # comparing naive (with no UTC offset) datetimes
    return remote_file_date > local_file_date


def ftp_get_md5(host, remote_path):
    f = FTP(host)
    f.login()
    m = hashlib.md5()
    f.retrbinary('RETR %s' % remote_path, m.update)
    return m.hexdigest()


def get_ftp_files(host):
    with FTP(host) as ftp:
        ftp.login()
        files = ftp.nlst()  # get files name within the directory
        return files

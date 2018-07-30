"""
Script to download gtfs from MOT ftp and upload to S3 bucket.
To use the script create a config file. see example /conf/gtfs_download.config.example
Provide in command line args the path to config file
"""
import ftplib
from configparser import ConfigParser
# from boto3.session import Session
from ftplib import FTP
import datetime
import time
import hashlib
import os
import argparse
import re
import pickle
import operator
# import pytz
import logging
import logging.config
import pathlib
import tempfile

"""
 omerTODO - A general issue - I think the current md5 pickle is not a good method.
 First, if I understand correctly, the check is made against the whole history,
 but I think we only care about changes made to the latest file with the same name.
 For example, if one day they add a line to a file, the next day delete it,
 and on the third day they put it back in, we will be missing that third day file with no possibility to know.
 Second, what happens if the pickle gets corrupted?
"""
# omerTODO - use tempfile for EVERY download
# omerTODO - only save md5 of the LAST downloaded file (by type)

"""
Based on http://docs.python.org/howto/logging.html#configuring-logging
"""
# logging.config.fileConfig('logging.conf')
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger("default")

MOT_FTP = 'gtfs.mot.gov.il'
# PICKLE_FILE_NAME = 'gtfs-downloads-pickle.p'
PICKLE_FILE_NAME = 'ftp-downloads-pickle.p'
GTFS_FILE_NAME = 'israel-public-transportation.zip'
CLUSTER_TO_LINE_FILE_NAME = 'ClusterToLine.zip'
TARIFF_FILE_NAME = 'Tariff.zip'
TRAIN_OFFICE_FILE_NAME = 'TrainOfficeLineId.zip'
TRIP_ID_FILE_NAME = 'TripIdToDate.zip'
ZONES_FILE_NAME = 'zones.zip'
DEBUG_FILE_NAME = CLUSTER_TO_LINE_FILE_NAME


def get_utc_date():
    """ return UTC date to timestamp folders """
    t = datetime.datetime.utcnow()
    return t.strftime('%Y-%m-%d')


def get_local_date_and_time_hyphen_delimited():
    """ return current time """
    t = datetime.datetime.now()
    return t.strftime('%Y-%m-%d-%H-%M-%S')


def ftp_get_file(local_path, host, remote_file_name):
    """ get file remote_file_name from FTP host and copy it into local_path """
    logger.info("Starting to download '%s' from host '%s' => '%s'" % (remote_file_name, host, local_path))
    try:
        f = FTP(host)
        f.login()
        fh = open(local_path, 'wb')
        f.retrbinary('RETR %s' % remote_file_name, fh.write)
        fh.close()
        f.quit()
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


def get_ftp_filenames(host):
    ftp = FTP(host)
    ftp.login()
    filenames = ftp.nlst()  # get filenames within the directory

    # for filename in filenames:
    #     local_filename = os.path.join('C:\\test\\', filename)
    #     file = open(local_filename, 'wb')
    #     ftp.retrbinary('RETR ' + filename, file.write)
    #
    #     file.close()
    #
    # ftp.quit()  # This is the “polite” way to close a connection
    return filenames


def md5_for_file(path, block_size=4096):
    """
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)
    """
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()


def connect_to_bucket(aws_args):
    from boto3.session import Session

    session = Session(aws_access_key_id=aws_args['aws_access_key_id'],
                      aws_secret_access_key=aws_args['aws_secret_access_key'])
    s3 = session.resource("s3")
    bucket = s3.Bucket(aws_args['bucket_url'])
    return bucket


def parse_config(config_file_name):
    with open(config_file_name) as f:
        # add section header because config parser requires it
        config_file_content = '[Section]\n' + f.read()
    config = ConfigParser()
    config.read_string(config_file_content)
    keys = ["aws_access_key_id", "aws_secret_access_key", "bucket_url"]
    config_dict = {key: config['Section'][key] for key in keys}
    return config_dict


def download_file_and_upload_to_s3_bucket(connection, remote_file_name, force=False):
    """ download remote file from mot, and upload to s3 Bucket """
    # filename = os.path.splitext(remote_file_name)[0] + datetime.datetime.now().strftime(
    #     '_%Y-%m-%dT%H-%M-%S') + pathlib.Path(remote_file_name).suffix
    filename = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S_') + remote_file_name

    logger.info("Downloading '%s' to temp file..." % remote_file_name)
    file_path_temp = tempfile.NamedTemporaryFile(prefix=datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S_') + remote_file_name, delete=False)
    # closing file for now, will re-open when needed
    file_path_temp.close()
    file_path = file_path_temp.name

    ftp_get_file(file_path, MOT_FTP, remote_file_name)

    if not force:
        tmp_md5 = md5_for_file(file_path)
        try:
            # check if identical file already exists - retrieve current md5 of zip with same name
            last_md5 = connection.Object(filename).e_tag[1:-1]  # boto3 relives with ""
            if str(last_md5) == tmp_md5:
                logger.debug("Checksum's are identical - removing tmp file...")
    			# remove tmp file
                os.unlink(file_path)
                return None
        except Exception as e:
            # file didn't exists
            pass

    logger.debug('No file exists yet, checksum for latest is different or force enabled -> copying...')

    # upload to bucket
    data = open(file_path, 'rb')
    connection.put_object(Key=filename, Body=data)
    data.close()

    # remove tmp file
    os.unlink(file_path)
    logger.info("'%s' retrieved to bucket" % remote_file_name)
    # print("Downloading '%s' to tmp file..." % remote_file_name)
    return


def upload_file_to_s3_bucket(connection, file_name, force=False):
    """ download gtfs zip file from mot, and upload to s3 Bucket """

    # upload to bucket
    data = open(file_name, 'rb')
    connection.put_object(Key=file_name, Body=data)
    data.close()

    return


def save_and_dump_pickle_dict(filename, timestamp_datetime, md5, dl_files_dict):
    """" Save a dictionary into a pickle file """
    """{'name', [milliseconds, 'md5']}"""
    temp_list = [filename, timestamp_datetime]
    dl_files_dict[md5] = temp_list
    dump_to_pickle_dict(dl_files_dict)


def dump_to_pickle_dict(dl_files_dict):
    # Save a dictionary into a pickle file
    pickle.dump(dl_files_dict, open(PICKLE_FILE_NAME, "wb"))


def print_dl_files_dict(dl_files_dict):
    for keys, values in dl_files_dict.items():
        logger.debug("md5 hash: " + keys)
        logger.debug("[filename, epoch in seconds]: ", values)


def load_pickle_dict(path):
    # Load the dictionary back from the pickle file.
    dl_files_dict = {}

    try:
        dl_files_dict = pickle.load(open(os.path.abspath(os.path.join(path, PICKLE_FILE_NAME)), "br"))
    except FileNotFoundError:
        ''' if the pickle file doesn't exist, create and init one '''
        open(os.path.abspath(os.path.join(path, PICKLE_FILE_NAME)), "wb")
        pickle.dump(dl_files_dict, open(os.path.abspath(os.path.join(path, PICKLE_FILE_NAME)), "wb"))

    # debug start
    # dl_files_dict["18739asdcsdfasd48a2518546a69f19"] = ["2018-02-25-13-08-57.zip", 1519570537]
    # dl_files_dict["djkca6b1a814e5b48a2518546a69f19"] = ["2018-02-22-13-08-57.zip", 1519470037]
    # debug end

    return dl_files_dict


def check_if_path_exists(path):
    """" check if path exists, if not, return cwd """
    if not os.path.exists(path):
        logger.error("ERROR: the path '" + path + "' does not exist, setting destination path to " + os.getcwd())
        path = os.getcwd()
    return path


def subset_of_dict_by_filename_prefix(full_dict, filename):
    # cropping file extension
    subset_dict = {}

    for key, value in full_dict.items():  # iter on both keys and values
        if value[0].startswith(os.path.splitext(filename)[0]):
            # print(key, value)
            subset_dict[key] = value
    return subset_dict


def download_file(dest_dir, remote_file_name, force_download):
    epoch_now = int(time.time())
    filename = os.path.splitext(remote_file_name)[0] + datetime.datetime.now().strftime(
        '-%Y-%m-%dT%H-%M-%S') + '.zip'

    dl_files_dict = load_pickle_dict(dest_dir)
    file_path = os.path.abspath(os.path.join(dest_dir, filename))

    # get the maximum value of epoch time in all dictionary
    try:
        subset_dict = subset_of_dict_by_filename_prefix(dl_files_dict, remote_file_name)
        # print(subset_dict)
        latest_local_timestamp = max(subset_dict.items(), key=operator.itemgetter(1))[1][1]
    except ValueError:
        # if dict is empty set timestamp to 1000000 which is equals to: 1970-01-12 15:46:40
        latest_local_timestamp = 1000000

    # if get_uptodateness(latest_local_timestamp, MOT_FTP, remote_file_name) or args.force_download:
    if get_uptodateness(latest_local_timestamp, MOT_FTP, remote_file_name) or force_download:
        logger.debug("New file have been found on " + MOT_FTP + " or the '-f' flag is on")
        ftp_get_file(file_path, MOT_FTP, remote_file_name)
        file_md5 = md5_for_file(file_path)
        # check if md5 already exists and add it if not
        if not (file_md5 in dl_files_dict):
            save_and_dump_pickle_dict(filename, epoch_now, file_md5, dl_files_dict)
        else:
            logger.debug(
                "The downloaded file '" + remote_file_name + "' already exists (according to md5 check), removing")
            os.remove(file_path)
    else:
        logger.debug("No newer (timestamp comparing) file have been found on FTP server")

    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aws", type=str, dest='aws_config_file_name', help="upload current MOT FTP content to AWS S3 "
                                                                             "See /conf/gtfs_download.config.example "
                                                                             "for a template for the configuration file"
                        )
    parser.add_argument("-d", dest='destination_directory', metavar='DIRECTORY', help="download to local library")
    parser.add_argument("-f", dest='force_download', action='store_true',
                        help="skip timestamp comparing and force download from ftp")
    parser.add_argument("-p", "--print", dest='print_inventory', metavar='DIRECTORY',
                        help="print saved details about files name, hash and epoch time")
    parser.add_argument("--print_ftp", action='store_true',
                        help="list all files on MOT's FTP")

    # parser.print_help()
    args = parser.parse_args()

    ftp_filenames_array = [GTFS_FILE_NAME, CLUSTER_TO_LINE_FILE_NAME, TARIFF_FILE_NAME, TRAIN_OFFICE_FILE_NAME,
                           TRIP_ID_FILE_NAME, ZONES_FILE_NAME]

    if args.aws_config_file_name:
        # remote_file_name = TRIP_ID_FILE_NAME
        args = parse_config(args.aws_config_file_name)
        # omerTODO - what if there is a new file in the ftp that is not in the list?
        filenames_on_ftp_array = get_ftp_filenames(MOT_FTP)
        for remote_file_name in filenames_on_ftp_array:
            connection = connect_to_bucket(args)
            download_file_and_upload_to_s3_bucket(connection, remote_file_name)

    if args.destination_directory:
        # remote_file_name = TARIFF_FILE_NAME
        filenames_on_ftp_array = get_ftp_filenames(MOT_FTP)
        for remote_file_name in filenames_on_ftp_array:
            dest_dir = check_if_path_exists(args.destination_directory)
            download_file(dest_dir, remote_file_name, args.force_download)

    if args.print_inventory:
        dest_dir = check_if_path_exists(args.print_inventory)
        print_dl_files_dict(load_pickle_dict(dest_dir))

    if args.print_ftp:
        filenames_on_ftp = get_ftp_filenames(MOT_FTP)
        print(filenames_on_ftp)

    return


if __name__ == '__main__':
    main()

"""
Script to download gtfs from MOT ftp and upload to S3 bucket.
To use the script create a config file. see example /conf/gtfs_download.config.example
Provide in command line args the path to config file
"""

from configparser import ConfigParser
from boto3.session import Session
from ftplib import FTP
import datetime
import time
import hashlib
import os
import argparse
import re
import pickle
import operator
import pytz

MOT_FTP = 'gtfs.mot.gov.il'
FILE_NAME = 'israel-public-transportation.zip'
DEBUG_FILE_NAME = 'Tariff.zip'
PICKLE_FILE_NAME = 'gtfs-downloads-pickle.p'


def get_utc_date():
    """ return UTC date to timestamp folders """
    t = datetime.datetime.utcnow()
    return t.strftime('%Y-%m-%d')


def get_local_date_and_time_hyphen_delimited():
    """ return current time """
    t = datetime.datetime.now()
    return t.strftime('%Y-%m-%d-%H-%M-%S')


def ftp_get_file(local_path, host = MOT_FTP, remote_path = DEBUG_FILE_NAME):
    """ get file remote_name from FTP host host and copied it into local_path"""
    f = FTP(host)
    f.login()
    fh = open(local_path, 'wb')
    f.retrbinary('RETR %s' % remote_path, fh.write)
    fh.close()
    f.quit()
    print("Retrieved from host %s: %s => %s" % (host, remote_path, local_path))


def get_uptodateness(local_timestamp, host = MOT_FTP, remote_file_name = FILE_NAME):
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
    session = Session(aws_access_key_id = aws_args['aws_access_key_id'],
                      aws_secret_access_key = aws_args['aws_secret_access_key'])
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


def upload_gtfs_file_to_s3_bucket(connection, force=False):
    """ download gtfs zip file from mot, and upload to s3 Bucket """
    file_name = get_utc_date() + '.zip'
    tmp_file = '/tmp/' + file_name

    print('Downloading GTFS to tmp file...')
    ftp_get_file(MOT_FTP, FILE_NAME, tmp_file)

    if not force:
        tmp_md5 = md5_for_file(tmp_file)
        try:
            # check if identical file already exists - retrieve current md5 of zip with same name
            last_md5 = connection.Object(file_name).e_tag[1:-1]  # boto3 relives with ""
            if str(last_md5) == tmp_md5:
                print("Checksum's are identical - removing tmp file...")
                os.remove(tmp_file)
                return None
        except Exception as e:
            # file didn't exists
            pass

    print('No file exists yet, checksum for latest is different or force enabled -> copying...')

    # upload to bucket
    data = open(tmp_file, 'rb')
    connection.put_object(Key=file_name, Body=data)
    data.close()
    
    # remove tmp file
    os.remove(tmp_file)
    print('GTFS file retrieved to bucket')
    return


def save_and_dump_pickle_dict(filename, timestamp_datetime, md5, dl_files_dict):
    """" Save a dictionary into a pickle file """
    #     favorite_color = { "lion": "yellow", "kitty": "red" }
    """{'name', [milliseconds, 'md5']}"""
    temp_list = [filename, timestamp_datetime]
    dl_files_dict[md5] = temp_list
    dump_to_pickle_dict(dl_files_dict)


def dump_to_pickle_dict(dl_files_dict):
    # Save a dictionary into a pickle file
    pickle.dump(dl_files_dict, open(PICKLE_FILE_NAME, "wb"))


def print_dl_files_dict(dl_files_dict):
    for keys, values in dl_files_dict.items():
        print("md5 hash: " + keys)
        print("[filename, epoch in seconds]: ", values)


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
        print("ERROR: the path '" + path + "' does not exist, setting destination path to " + os.getcwd())
        path = os.getcwd()
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aws", type=str, dest='aws_config_file_name', help="download to AWS. "
                        "See /conf/gtfs_download.config.example for a template for the configuration file")
    parser.add_argument("-d", dest='destination_directory', metavar='DIRECTORY', help="download to local library")
    parser.add_argument("-f", dest='force_download', action='store_true', help="skip timestamp comparing and force download from ftp")
    parser.add_argument("-p", "--print", dest='print_inventory', metavar='DIRECTORY', help="print saved details about files name, hash and epoch time")

    # parser.print_help()
    args = parser.parse_args()

    if args.aws_config_file_name:
        print("got --aws")
        args = parse_config(args.aws_config_file_name)
        connection = connect_to_bucket(args)
        upload_gtfs_file_to_s3_bucket(connection)

    if args.destination_directory:
        print("got -d")
        epoch_now = int(time.time())
        filename = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.zip'

        dest_dir = check_if_path_exists(args.destination_directory)

        dl_files_dict = load_pickle_dict(dest_dir)
        file_path = os.path.abspath(os.path.join(dest_dir, filename))

        # get the maximum value of epoch time in all dictionary
        try:
            latest_local_timestamp = max(dl_files_dict.items(), key=operator.itemgetter(1))[1][1]
        except ValueError:
            # if dict is empty set to 0
            latest_local_timestamp = 1000000 # equals to: 1970-01-12 15:46:40

        if get_uptodateness(latest_local_timestamp, MOT_FTP, DEBUG_FILE_NAME) or args.force_download:
            print("new file have been found on " + MOT_FTP + " or '-f' flag is on")
            ftp_get_file(file_path, MOT_FTP, DEBUG_FILE_NAME)
            file_md5 = md5_for_file(file_path)
            # check if md5 already exists and add it if so
            if not (file_md5 in dl_files_dict):
                save_and_dump_pickle_dict(filename, epoch_now, file_md5, dl_files_dict)
            else:
                print("the downloaded file already exists (according to md5 check), removing")
                os.remove(file_path)

    if args.print_inventory:
        dest_dir = check_if_path_exists(args.print_inventory)
        print_dl_files_dict(load_pickle_dict(dest_dir))
    return


if __name__ == '__main__':
    main()

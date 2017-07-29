"""
Script to download gtfs from MOT ftp and upload to S3 bucket.
To use the script create a config file. see example /conf/gtfs_download.config.example
Provide in command line args the path to config file
"""

from configparser import ConfigParser
from boto3.session import Session
from sys import argv
from ftplib import FTP
import datetime
import hashlib
import os

MOT_FTP = 'gtfs.mot.gov.il'
FILE_NAME = 'israel-public-transportation.zip'


def get_utc_time_underscored():
    """ return UTC time as underscored, to timestamp folders """
    t = datetime.datetime.utcnow()
    return t.strftime('%Y-%m-%d')


def ftp_get_file(host, remote_path, local_path):
    """ get file remote_name from FTP host host and copied it inot local_path"""
    f = FTP(host)
    f.login()
    fh = open(local_path, 'wb')
    f.retrbinary('RETR %s' % (remote_path), fh.write)
    fh.close()
    f.quit()
    print("Retrieved from host %s: %s => %s" % (host, remote_path, local_path))


def md5_for_file(path, block_size=4096):
    """
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)
    """
    md5 = hashlib.md5()
    with open(path,'rb') as f:
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


def download_gtfs_file(connection, force=False):
    """ download gtfs zip file from mot, and upload to s3 Bucket """
    file_name = get_utc_time_underscored() + '.zip'
    tmp_file = '/tmp/' + file_name

    print('Downloading GTFS to tmp file...')
    ftp_get_file(MOT_FTP, FILE_NAME, tmp_file)

    if not force:
        tmp_md5 = md5_for_file(tmp_file)
        try:
            # check if identical file already exists - retrieve current md5 of zip with same name
            last_md5 = connection.Object(file_name).e_tag[1:-1]  # boto3 retrives with ""
            if str(last_md5) == tmp_md5:
                print('Checksums are identical - removing tmp file...')
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


def main():
    if len(argv) < 2:
        print("Usage: %s config_file_name" % os.path.basename(__file__))
        print("See /conf/gtfs_download.config.example for a template for the configuration file")
        return
    args = parse_config(argv[1])
    connection = connect_to_bucket(args)
    download_gtfs_file(connection)


if __name__ == '__main__':
    main()

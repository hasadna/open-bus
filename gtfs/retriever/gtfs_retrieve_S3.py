import os
import logging.config
from configparser import ConfigParser
from boto3.session import Session

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger("default")


def connect_to_bucket(aws_args):
    session = Session(aws_access_key_id=aws_args['aws_access_key_id'],
                      aws_secret_access_key=aws_args['aws_secret_access_key'])
    s3 = session.resource("s3")
    bucket = s3.Bucket(aws_args['bucket_url'])
    return bucket


def upload_file_to_s3_bucket(connection, file_path, filename_in_bucket):
    """ upload 'file_name' to s3 Bucket """

    # upload to bucket
    try:
        data = open(file_path, 'rb')
        connection.put_object(Key=filename_in_bucket, Body=data)
        data.close()
        logger.info("'%s' uploaded to bucket successfully as '%s'" % (file_path, filename_in_bucket))
    except IOError as e:
        logger.error("Error uploading '%s' to bucket: %s" % (file_path, e))


def parse_s3_config_file(config_file_path):
    with open(config_file_path) as f:
        # add section header because config parser requires it
        config_file_content = '[Section]\n' + f.read()
    config = ConfigParser()
    config.read_string(config_file_content)
    keys = ["aws_access_key_id", "aws_secret_access_key", "bucket_url"]
    config_dict = {key: config['Section'][key] for key in keys}
    return config_dict

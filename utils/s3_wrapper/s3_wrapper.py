import sys
import boto3
import argparse


def _get_bucket(access_key_id, secret_access_key, bucket_name):
    return boto3.resource('s3',
                          aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key,
                          endpoint_url='https://ams3.digitaloceanspaces.com') \
        .Bucket(bucket_name)


def _upload_one_file_to_cloud(local_file, cloud_key, bucket):
    bucket.upload_file(local_file, cloud_key)


def _download_one_file(local_file, cloud_key, bucket):
    bucket.download_file(cloud_key, local_file)


def upload(access_key_id, secret_access_key, bucket_name, local_file, cloud_key):
    bucket = _get_bucket(access_key_id, secret_access_key, bucket_name)
    _upload_one_file_to_cloud(local_file, cloud_key, bucket)


def download(access_key_id, secret_access_key, bucket_name, local_file, cloud_key):
    bucket = _get_bucket(access_key_id, secret_access_key, bucket_name)
    _download_one_file(local_file, cloud_key, bucket)


def cli(args):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest="command")
    # create the parser for the "upload" command
    parser_upload = subparsers.add_parser('upload', help='Upload a file from local machine to cloud', )
    parser_upload.add_argument('--access-key-id', '-aki', dest='access_key_id',
                               help='access key id from S3 provider', metavar='<String>', required=True)
    parser_upload.add_argument('--secret-access-key', '-sak', dest='secret_access_key',
                               help='secret access key from S3 provider', metavar='<String>', required=True)
    parser_upload.add_argument('--local-file', '-lf', dest='local_file', metavar='<Path>', required=True,
                               help='reference for local file you wish to upload to path to download to')
    parser_upload.add_argument('--key', '-k', dest='cloud_key', required=True, metavar='<Path>',
                               help='key of a file in S3')
    parser_upload.add_argument('--bucket-name', '-bn', dest='bucket_name',
                               help='bucket name in s3. (default: obus-do1)', metavar='<String>', default='obus-do1')
    # create the parser for the "download" command
    parser_download = subparsers.add_parser('download', help='Download a file from cloud to local machine ')
    parser_download.add_argument('--access-key-id', '-aki', dest='access_key_id', required=True,
                                 help='access key id from S3 provider', metavar='<String>')
    parser_download.add_argument('--secret-access-key', '-sak', dest='secret_access_key', required=True,
                                 help='secret access key from S3 provider', metavar='<String>')
    parser_download.add_argument('--local-file', '-lf', dest='local_file',
                                 help='reference for local file you wish to upload to path to download to',
                                 metavar='<Path>', required=True)
    parser_download.add_argument('--key', '-k', dest='cloud_key', required=True, help='key of a file in S3',
                                 metavar='<Path>')
    parser_download.add_argument('--bucket-name', '-bn', dest='bucket_name',
                                 help='bucket name in s3. (default: obus-do1)', metavar='<String>', default='obus-do1')

    return parser.parse_args(args)


def main(argv):
    args = cli(argv)
    if args.command == 'upload':
        upload(args.access_key_id, args.secret_access_key, args.bucket_name, args.local_file, args.cloud_key)
    elif args.command == 'download':
        download(args.access_key_id, args.secret_access_key, args.bucket_name, args.local_file, args.cloud_key)


if __name__ == "__main__":
    main(sys.argv[1:])

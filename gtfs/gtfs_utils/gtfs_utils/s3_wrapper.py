#!/usr/bin/python3
import argparse
import fnmatch
import os
import re
import sys
import logging
import boto3
import botocore.exceptions
from types import MappingProxyType
from typing import Callable, List, Tuple
from .configuration import S3Configuration

_AWS = 'aws'
_DIGITALOCEAN_PUBLIC = 'dig-public'
_DIGITALOCEAN_PRIVATE = 'dig-private'

_DIGITALOCEAN_ENDPOINT = 'https://ams3.digitaloceanspaces.com'

_DEFAULTS = MappingProxyType({_AWS: {'bucket_name': 's3.obus.hasadna.org.il'},
                              _DIGITALOCEAN_PRIVATE: {'bucket_name': 'obus-do1',
                                                      'endpoint_url': _DIGITALOCEAN_ENDPOINT},
                              _DIGITALOCEAN_PUBLIC: {'bucket_name': 'obus-do2',
                                                     'endpoint_url': _DIGITALOCEAN_ENDPOINT}})


class S3Crud:
    def __init__(self, **conn_args):
        self.bucket_name = conn_args.get('bucket_name')
        assert self.bucket_name is not None

        conn_args.pop('bucket_name')

        self.client = boto3.session.Session().client('s3', **conn_args)

    @classmethod
    def from_configuration(cls, s3_configuration: S3Configuration):
        return cls(aws_access_key_id=s3_configuration.access_key_id,
                   aws_secret_access_key=s3_configuration.secret_access_key,
                   bucket_name=s3_configuration.bucket_name,
                   endpoint_url=s3_configuration.s3_endpoint_url)


    def upload_one_file(self, local_file: str, cloud_key: str) -> None:
        self.client.upload_file(Filename=local_file, Key=cloud_key, Bucket=self.bucket_name)

    def download_one_file(self, local_file: str, cloud_key: str, callback: Callable = None) -> None:
        logging.info(f'Downloading { cloud_key } into { local_file }')
        os.makedirs(os.path.split(local_file)[0], exist_ok=True)
        self.client.download_file(Filename=local_file,
                                  Key=cloud_key,
                                  Bucket=self.bucket_name,
                                  Callback=callback)

    def list_bucket_files(self, prefix_filter: str) -> List:
        return self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix_filter).get('Contents', [])

    def get_file_size(self, file_key: str):
        return self.client.head_object(Bucket=self.bucket_name, Key=file_key)['ContentLength']

    def is_key_exist(self, key_name: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key_name)

        except botocore.exceptions.ClientError as e:
            response_code = int(e.response['Error']['Code'])
            if response_code == 404:
                return False
            raise e
        return True

    def get_md5(self, key_name: str)-> str:
        return self.client.head_object(Bucket=self.bucket_name, Key=key_name)['ETag'].strip('"')


def _regex_filter(keys_metadata_items: List, regex_argument: str) -> list:
    """
    Filter list of strings by the given regex argument
    :param keys_metadata_items:
    :param regex_argument:
    :return: list of strings that pass the regex filter
    """
    regex = re.compile(regex_argument)
    return [itm for itm in keys_metadata_items if regex.search(itm['Key'])]


def list_content(crud: S3Crud, prefix_filter: str = '',
                 regex_argument: str = None, action: Callable = None) -> list:
    """
    This method uses the given CRUD object to get list of objects on S3
    :param crud:
    :param prefix_filter: filter keys that starts with given string
    :param regex_argument: filter keys by regex argument
    :param action: a callable to perform an action on found keys func(listOfKeys)
    :return: list of objects on S3
    :rtype: list
    """
    files = list(crud.list_bucket_files('' if not prefix_filter else prefix_filter))
    if regex_argument:
        files = _regex_filter(files, regex_argument)
    if action:
        action(files)
    return files


def _create_items_from_local_folder(is_folder: bool, local_path: str, key_name: str, filter_arg: str = '*') \
        -> List[Tuple[str, str]]:

    if not is_folder:
        return [(local_path, key_name)]

    return sorted([(os.path.join(local_path, file_name), '/'.join([key_name, file_name]))
                   for file_name
                   in os.listdir(local_path)
                   if fnmatch.fnmatch(file_name, filter_arg) and os.path.isfile(os.path.join(local_path, file_name))])


def upload(crud: S3Crud, local_file: str, key_name: str, is_folder: bool, filter_arg: str) -> None:
    """
    This method uses the given CRUD object to upload one file to the S3
    :rtype: None
    :param crud:
    :param local_file:
    :param key_name:
    :param is_folder:
    :param filter_arg:
    """
    items = _create_items_from_local_folder(is_folder, local_file, key_name, filter_arg if filter_arg else "*")
    for local_file, key_name in items:
        crud.upload_one_file(local_file, key_name)


def download(crud: S3Crud, local_file: str, key_name: str) -> None:
    """
    This method uses the given CRUD object to download one file from the S3
    :rtype: None
    :param crud:
    :param local_file:
    :param key_name:
    """
    crud.download_one_file(local_file, key_name)


def is_exist(crud: S3Crud, key_name: str) -> bool:
    """
    Check whether the given key name is exist in bucket or not
    :param crud:
    :param key_name:
    :return True if key exist in bucket:
    :rtype: bool
    """
    return crud.is_key_exist(key_name)


def parse_cli_arguments(args: List[str]) -> argparse.Namespace:
    """
    Parse and Validate the given cli arguments
    :param args: App arguments without the first argument with the execution path
    :return: a dict like object with the given arguments values
    """
    s3_access_parser = argparse.ArgumentParser(add_help=False)
    s3_access_parser.add_argument('--access-key-id', '-aki', dest='aws_access_key_id',
                                  help='access key id from S3 provider', metavar='<String>')
    s3_access_parser.add_argument('--secret-access-key', '-sak', dest='aws_secret_access_key',
                                  help='secret access key from S3 provider', metavar='<String>')
    s3_access_parser.add_argument('--bucket-name', '-bn', dest='bucket_name',
                                  help='bucket name in s3. (default: obus-do1)', metavar='<String>')
    s3_access_parser.add_argument('--endpoint-url', '-eu', dest='endpoint_url',
                                  help='End point url of s3 service (in case of Amazon there is no need to provide)',
                                  metavar='<String>')
    s3_access_parser.add_argument('--access-preset', '-ap', dest='access_preset',
                                  help='use access preset default values: [{} / {} / {}]'
                                       .format(_AWS, _DIGITALOCEAN_PRIVATE, _DIGITALOCEAN_PUBLIC))

    local_remote_keys_parser = argparse.ArgumentParser(add_help=False)
    local_remote_keys_parser.add_argument('--key', '-k', dest='cloud_key', required=True, metavar='<Path>',
                                          help='key of a file in S3')
    local_remote_keys_parser.add_argument('--local-file', '-lf', dest='local_file', metavar='<Path>', required=True,
                                          help='reference for local file you wish to upload to path to download to')

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest="command")
    # create the parser for the "upload" command
    parser_upload = subparsers.add_parser('upload', help='Upload a file from local machine to cloud',
                                          parents=[s3_access_parser, local_remote_keys_parser])
    parser_upload.add_argument('-fd', '--folder', action='store_true', dest='is_folder',
                               help='Add all files in a folder')
    parser_upload.add_argument('--path-filter', '-pf', dest='path_filter',
                               help='filter files path', metavar='<String>')
    # create the parser for the "download" command
    subparsers.add_parser('download', help='Download a file from cloud to local machine ',
                          parents=[s3_access_parser, local_remote_keys_parser])
    # create the parser for the "list" command
    parser_list = subparsers.add_parser('list', help='list files on cloud ', parents=[s3_access_parser])
    parser_list.add_argument('--prefix-filter', '-pf', dest='prefix_filter',
                             help='filter files that their path starts with the given string', metavar='<String>')
    parser_list.add_argument('--regex-filter', '-rf', dest='regex_filter',
                             help='filter files path by regex', metavar='<String>')

    return parser.parse_args(args)


def make_crud_args(args: argparse.Namespace,
                   presets: MappingProxyType = MappingProxyType({})):

    res = presets.get(args.access_preset, {})

    relevant_cli_arguments = {k: v for k, v in vars(args).items()
                              if k in ('aws_access_key_id',
                                       'bucket_name',
                                       'endpoint_url',
                                       'aws_secret_access_key') and v is not None}

    res.update(relevant_cli_arguments)

    return res


def main(argv):
    args = parse_cli_arguments(argv)
    crud_args = make_crud_args(args, _DEFAULTS)

    crud = S3Crud(**crud_args)

    if args.command == 'upload':
        upload(crud, args.local_file, args.cloud_key, args.is_folder, args.path_filter)
    elif args.command == 'download':
        download(crud, args.local_file, args.cloud_key)
    elif args.command == 'list':
        list_content(crud, args.prefix_filter, args.regex_filter, _print_long_files_metadata)


def _sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0


def _print_long_files_metadata(s3_objs: List):
    s3_objs.sort(key=lambda x: x['Key'], reverse=True)
    for itm in s3_objs:
        s = "{}\t{}\t{}".format(itm['LastModified'], _sizeof_fmt(itm['Size']), itm['Key'])
        print(s)


if __name__ == "__main__":
    main(sys.argv[1:])

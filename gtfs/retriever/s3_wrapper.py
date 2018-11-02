import re
import sys
import boto3
import argparse
import os
import fnmatch
from typing import Callable, List, Generator, Any, Tuple


class S3Crud:
    def __init__(self, access_key_id, secret_access_key, bucket_name,
                 endpoint_url='https://ams3.digitaloceanspaces.com'):
        self.bucket = boto3.resource('s3',
                                     aws_access_key_id=access_key_id,
                                     aws_secret_access_key=secret_access_key,
                                     endpoint_url=endpoint_url).Bucket(bucket_name)

    def upload_one_file(self, local_file: str, cloud_key: str) -> None:
        self.bucket.upload_file(local_file, cloud_key)

    def download_one_file(self, local_file: str, cloud_key: str) -> None:
        self.bucket.download_file(cloud_key, local_file)

    def list_bucket_files(self, prefix_filter: str) -> Generator[str, None, None]:
        gen = self.bucket.objects.filter(Prefix=prefix_filter)
        return S3Crud._convert_s3_gen_into_key_name_gen(gen)

    def is_key_exist(self, key_name: str) -> bool:
        for curr_key_name in self.list_bucket_files(key_name):
            if curr_key_name == key_name:
                return True
        return False

    @staticmethod
    def _convert_s3_gen_into_key_name_gen(gen: Generator[Any, None, None]) \
            -> Generator[str, None, None]:
        for s3_obj in gen:
            yield s3_obj.key


def _regex_filter(strings: list, regex_argument: str) -> list:
    """
    Filter list of strings by the given regex argument
    :param strings:
    :param regex_argument:
    :return: list of strings that pass the regex filter
    """
    return list(filter(re.compile(regex_argument).search, strings))


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

    return[(os.path.join(local_path, fname), '/'.join([key_name, fname]))
           for fname
           in os.listdir(local_path)
           if fnmatch.fnmatch(fname, filter_arg)]


def upload(crud: S3Crud, local_file: str, key_name: str, is_folder: bool, filter_arg: str) -> None:
    """
    This method uses the given CRUD object to upload one file to the S3
    :rtype: None
    :param crud:
    :param local_file:
    :param key_name:
    :param is_folder:
    """
    items = _create_items_from_local_folder(is_folder, local_file, key_name, filter_arg)

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
    parser_upload.add_argument('-fd', '--folder', action='store_true', dest='is_folder',
                               help='Add all files in a folder')
    parser_upload.add_argument('--path-filter', '-pf', dest='path_filter',
                               help='filter files path', metavar='<String>')
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
    # create the parser for the "list" command
    parser_list = subparsers.add_parser('list', help='list files on cloud ')
    parser_list.add_argument('--access-key-id', '-aki', dest='access_key_id',
                             help='access key id from S3 provider', metavar='<String>', required=True)
    parser_list.add_argument('--secret-access-key', '-sak', dest='secret_access_key',
                             help='secret access key from S3 provider', metavar='<String>', required=True)
    parser_list.add_argument('--bucket-name', '-bn', dest='bucket_name',
                             help='bucket name in s3. (default: obus-do1)', metavar='<String>', default='obus-do1')
    parser_list.add_argument('--prefix-filter', '-pf', dest='prefix_filter',
                             help='filter files that thier path starts with the given string', metavar='<String>')
    parser_list.add_argument('--regex-filter', '-rf', dest='regex_filter',
                             help='filter files path by regex', metavar='<String>')

    return parser.parse_args(args)


def main(argv):
    args = parse_cli_arguments(argv)
    crud = S3Crud(args.access_key_id, args.secret_access_key, args.bucket_name)
    if args.command == 'upload':
        upload(crud, args.local_file, args.cloud_key, args.is_folder, args.path_filter)
    elif args.command == 'download':
        download(crud, args.local_file, args.cloud_key)
    elif args.command == 'list':
        list_content(crud, args.prefix_filter, args.regex_filter, print)


if __name__ == "__main__":
    main(sys.argv[1:])

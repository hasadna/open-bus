import json
import os
import re
import sys
from dataclasses import dataclass, fields, is_dataclass, field
from inspect import isclass
from typing import Dict, List

from jsonschema import validate

CONFIGURATION_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
CONFIGURATION_SCHEMA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config.schema.json')


@dataclass
class ChildDirectories:
    gtfs_feeds: str = None
    output: str = None
    filtered_feeds: str = None
    logs: str = None


@dataclass
class FullPaths:
    gtfs_feeds: str = None
    output: str = None
    filtered_feeds: str = None
    logs: str = None

    def all(self) -> List[str]:
        """
        Returns a list with the paths of all of the directories
        :return: a path list
        """
        return list(vars(self).values())


@dataclass
class FilesConfiguration:
    base_directory: str = None
    child_directories: ChildDirectories = None
    output_file_name_regexp: str = None
    output_file_type: str = None

    def __init__(self):
        self.__full_paths = None

    @property
    def full_paths(self) -> FullPaths:
        if not self.__full_paths and self.child_directories:
            self.__full_paths = FullPaths()
            for dir_name, dir_path in vars(self.child_directories).items():
                setattr(self.__full_paths, dir_name, os.path.join(self.base_directory, dir_path))

        return self.__full_paths


@dataclass
class S3Configuration:
    access_key_id: str = None
    secret_access_key: str = None
    s3_endpoint_url: str = None
    bucket_name: str = None
    upload_results: bool = False
    results_path_prefix: str = ''


@dataclass
class Configuration:
    files: FilesConfiguration = None
    s3: S3Configuration = None
    use_data_from_today: bool = True
    date_range: List[str] = field(default_factory=list)
    max_gtfs_size_in_mb: int = sys.maxsize
    display_download_progress_bar: bool = True
    display_size_on_progress_bar: bool = True
    delete_downloaded_gtfs_zip_files: bool = True
    write_filtered_feed: bool = True
    console_verbosity: str = 'ERROR'


def dict_to_dataclass(data_dict: Dict, data_class: type) -> Configuration:
    """
    Converts the dict to a dataclass instance of the given type.
    """
    data_class_instance = data_class()

    for field in fields(data_class):
        if field.name not in data_dict:
            continue  # The value is already set by default value of the class
        else:
            if isclass(field.type) and is_dataclass(field.type):
                value = dict_to_dataclass(data_dict[field.name], field.type)
            elif field.type == re.Pattern:
                value = re.compile(data_dict[field.name])
            else:
                value = data_dict[field.name]

        if isinstance(field.type, type):
            if not isinstance(value, field.type):
                raise TypeError(f'Configuration field \'{field.name}\' '
                                f'should be of type {field.type.__name__}, '
                                f'but is actually of type {type(value).__name__}')
        elif not isinstance(value, field.type.__origin__):
                raise TypeError(f'Configuration field \'{field.name}\' '
                                f'should be of type {field.type.__origin__.__name__}, '
                                f'but is actually of type {type(value).__name__}')

        setattr(data_class_instance, field.name, value)

    return data_class_instance


def validate_configuration_schema(configuration_dict: dict) -> None:
    """
    Validate the configuration dict against the configuration JSON Schema
    :param configuration_dict: a dict of the configuration, as loaded with json.load
    :return: raises an error (jsonschema.exceptions.ValidationError)
    """
    with open(CONFIGURATION_SCHEMA_FILE_PATH, 'r') as schema_file:
        config_schema = json.load(schema_file)
    # The definitions are separated to a different key,
    # so it won't appear in the sphinx generated docs
    schema = config_schema['schema']
    schema['definitions'] = config_schema['definitions']
    validate(instance=configuration_dict, schema=schema)


def load_configuration() -> Configuration:
    with open(CONFIGURATION_FILE_PATH, 'r') as configuration_file:
        configuration_dict = json.load(configuration_file)
    validate_configuration_schema(configuration_dict)
    return dict_to_dataclass(configuration_dict, Configuration)


configuration = load_configuration()

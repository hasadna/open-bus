from dataclasses import dataclass, fields, is_dataclass, field
import json
import os
import re
from inspect import isclass
from typing import Dict, List


CONFIGURATION_FILE_PATH  = os.path.join(os.path.dirname(__file__), 'config.json')


@dataclass
class ChildDirectories:
    archive: str = None
    gtfsFeeds: str = None
    output: str = None
    filteredFeeds: str = None
    logs: str = None


@dataclass
class FullPaths:
    archive: str = None
    gtfsFeeds: str = None
    output: str = None
    filteredFeeds: str = None
    logs: str = None

    def all(self) -> List[str]:
        """
        Returns a list with the paths of all of the directories
        :return: a path list
        """
        return list(vars(self).values())


@dataclass
class FilesConfiguration:
    baseDirectory: str = None
    childDirectories: ChildDirectories = None
    tariffFilePath: str = None
    outputFileNameRegexp: str = None

    def __init__(self):
        self.__full_paths = None

    @property
    def full_paths(self) -> FullPaths:
        if not self.__full_paths and self.childDirectories:
            self.__full_paths = FullPaths()
            for dir_name, dir_path in vars(self.childDirectories).items():
                setattr(self.__full_paths, dir_name, os.path.join(self.baseDirectory, dir_path))

        return self.__full_paths


@dataclass
class Configuration:
    files: FilesConfiguration = None
    bucketName: str = None
    bucketValidFileNameRegexp: re.Pattern = None
    forwardFill: bool = True
    futureDaysCount: int = 0
    displayDownloadProgressBar: bool = True
    displaySizeOnProgressBar: bool = True
    deleteDownloadedGtfsZipFiles: bool = True
    writeFilteredFeed: bool = True


def dict_to_dataclass(data_dict: Dict, data_class: type) -> Dict:
    """
    Converts the dict to a dataclass instance of the given type.
    """
    data_class_instance = data_class()

    for field in fields(data_class):
        if isclass(field.type) and is_dataclass(field.type):
            value = dict_to_dataclass(data_dict[field.name], field.type)
        elif field.type == re.Pattern:
            value = re.compile(data_dict[field.name])
        else:
            value = data_dict[field.name]

        if not isinstance(value, field.type):
            raise TypeError(f'Configuration field \'{field.name}\' '
                            f'should be of type {field.type.__name__}, '
                            f'but is actually of type {type(value).__name__}')

        setattr(data_class_instance, field.name, value)

    return data_class_instance


def load_configuration() -> Configuration:
    with open(CONFIGURATION_FILE_PATH, 'r') as configuration_file:
        configuration_dict = json.load(configuration_file)
    return dict_to_dataclass(configuration_dict, Configuration)


configuration = load_configuration()

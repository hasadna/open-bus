from dataclasses import dataclass, fields, is_dataclass
import json
import os
from inspect import isclass
from typing import Dict

CONFIGURATION_FILE_PATH  = os.path.join(os.path.dirname(__file__), 'config.json')


@dataclass
class ChildDirectories:
    dataDirectory: str = None
    archiveDirectory: str = None
    gtfsFeedsDirectory: str = None
    outputDirectory: str = None
    filteredFeedsDirectory: str = None
    logsDirectory: str = None


@dataclass
class LocalFiles:
    baseDirectory: str = None
    childDirectories: ChildDirectories = None
    tariffFilePath: str = None
    outputFileNameRegexp: str = None


@dataclass
class Configuration:
    localFiles: LocalFiles = None
    # TODO: add required fields here


def dict_to_dataclass(dirty_dict: Dict, data_class: type) -> Dict:
    """
    Clears the dict from fields that are not part of the
    """
    data_class_instance = data_class()

    for field in fields(data_class):
        if isclass(field.type) and is_dataclass(field.type):
            value = dict_to_dataclass(dirty_dict[field.name], field.type)
        else:
            value = dirty_dict[field.name]

        setattr(data_class_instance, field.name, value)

    return data_class_instance


def load_configuration() -> Configuration:
    with open(CONFIGURATION_FILE_PATH, 'r') as configuration_file:
        configuration_dict = json.load(configuration_file)
    return dict_to_dataclass(configuration_dict, Configuration)


configuration = load_configuration()

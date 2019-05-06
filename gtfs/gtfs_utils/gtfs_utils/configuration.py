from dataclasses import dataclass
import json
import os


CONFIGURATION_FILE_PATH  = os.path.join(os.path.dirname(__file__), 'config.json')


@dataclass
class Configuration:
    # TODO: add required fields here
    pass


def load_configuration() -> Configuration:
    with open(CONFIGURATION_FILE_PATH, 'r') as configuration_file:
        configuration_dict = json.load(configuration_file)
    # TODO: fix 'unexpected keyword argument' error when having fields in the json file that are not in the dataclass
    return Configuration(**configuration_dict)


configuration = load_configuration()

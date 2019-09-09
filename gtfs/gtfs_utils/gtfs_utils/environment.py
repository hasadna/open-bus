import os
from .configuration import configuration


def mkdir_if_not_exists(dir_path):
    """ Creates the directory if it does not exist """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def init_conf():
    """ Initializes directories from configuration file """
    mkdir_if_not_exists(configuration.files.base_directory)

    for dir_path in configuration.files.full_paths.all():
        mkdir_if_not_exists(dir_path)

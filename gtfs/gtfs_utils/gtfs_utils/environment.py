import os
from configuration import configuration


def mkdir_if_not_exists(dir_path):
    """ Creates the directory if it does not exist """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def init_conf():
    """ Initializes directories from configuration file """
    if not os.path.exists(configuration.files.baseDirectory):
        raise ValueError("Base directory does not exist")
    for dir_path in configuration.files.full_paths.all():
        mkdir_if_not_exists(dir_path)

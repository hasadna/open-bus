import os
from gtfs_utils.gtfs_utils import configuration


def mkdir_if_not_exists(dir_path):
    """ Creates the directory if it does not exist """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def init_conf():
    """ Initializes directories from configuration file """
    if not os.path.exists(configuration.localFiles.baseDirectory):
        raise ValueError("Base directory does not exist")
    for dir_path in configuration.localFiles.childDirectories.all():
        mkdir_if_not_exists(dir_path)

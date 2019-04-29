import os
from gtfs_stats_conf import *


def mkdir_if_not_exists(dir_path):
    """ Create the directory if it does not exist """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def init_conf():
    """ Init directories from conf file """
    if not os.path.exists(BASE_FOLDER):
        raise ValueError("Base folder does not exist")
    for dir_path in ALL_FOLDERS:
        mkdir_if_not_exists(dir_path)

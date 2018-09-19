import os
import logging.config
import pickle
import operator
import hashlib

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger("default")

PICKLE_FILE_NAME = 'ftp-downloads-pickle.p'


def save_and_dump_pickle_dict(remote_filename, local_filename, timestamp_datetime, md5, dl_files_dict):
    """ Save a dictionary into a pickle file """
    """{'name', [milliseconds, 'md5']}"""
    temp_list = [remote_filename, local_filename, timestamp_datetime]
    dl_files_dict[md5] = temp_list
    dump_to_pickle_dict(dl_files_dict)


def dump_to_pickle_dict(dl_files_dict):
    # Save a dictionary into a pickle file
    pickle.dump(dl_files_dict, open(PICKLE_FILE_NAME, "wb"))


def load_pickle_dict(path):
    # Load the dictionary back from the pickle file.
    dl_files_dict = {}

    try:
        dl_files_dict = pickle.load(open(os.path.abspath(os.path.join(path, PICKLE_FILE_NAME)), "br"))
    except FileNotFoundError:
        ''' if the pickle file doesn't exist, create and init one '''
        logger.debug("No pickle file have been found, creating one")
        open(os.path.abspath(os.path.join(path, PICKLE_FILE_NAME)), "wb")
        pickle.dump(dl_files_dict, open(os.path.abspath(os.path.join(path, PICKLE_FILE_NAME)), "wb"))

    # debug start
    # dl_files_dict["18739asdcsdfasd48a2518546a69f19"] = ["2018-02-25-13-08-57.zip", 1519570537]
    # dl_files_dict["djkca6b1a814e5b48a2518546a69f19"] = ["2018-02-22-13-08-57.zip", 1519470037]
    # debug end

    return dl_files_dict


def get_latest_local_timestamp(dl_files_dict, remote_file_name):
    # get the maximum value of epoch time in all dictionary
    # if dict is empty set timestamp to '0' which equals to: 1970-01-01 00:00:00
    latest_local_timestamp = 0
    subset_dict = subset_of_dict_by_filename_prefix(dl_files_dict, remote_file_name)
    if subset_dict:
        latest_local_timestamp = max(subset_dict.items(), key=operator.itemgetter(1))[1][2]
    logger.debug("latest_local_timestamp = %s", latest_local_timestamp)
    return latest_local_timestamp


def subset_of_dict_by_filename_prefix(full_dict, filename):
    # cropping file extension
    subset_dict = {}

    for key, value in full_dict.items():  # iter on both keys and values
        if value[0].startswith(os.path.splitext(filename)[0]):
            # print(key, value)
            subset_dict[key] = value
    return subset_dict


def check_if_path_exists(path):
    """" check if path exists, if not, return cwd """
    if not os.path.exists(path):
        logger.error("ERROR: the path '" + path + "' does not exist, setting destination path to " + os.getcwd())
        path = os.getcwd()
    return path


def md5_for_file(path, block_size=4096):
    """
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)
    """

    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

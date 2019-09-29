import os
import pickle
import hashlib

MIN_EPOCH_TIME = 86400

##################################
######## Pickle Managment ########
##################################

PICKLE_REL_PATH = '.retriever/metadata.p'
pickle_location = ''
obj = {}


def init(path):
    global obj, pickle_location
    obj = {}
    pickle_location = os.path.join(path, PICKLE_REL_PATH)

    if os.path.exists(pickle_location):
        _load_pickle()
    else:
        os.makedirs(os.path.join(path, '.retriever'), exist_ok=True)
        _dump_pickle()


def _load_pickle():
    global obj
    with open(pickle_location, "rb") as f:
        obj = pickle.load(f)


def _dump_pickle():
    with open(pickle_location, "wb") as f:
        pickle.dump(obj, f)


def _add(key, value):
    obj[key] = value
    _dump_pickle()


def _get(key):
    return obj.get(key, None)


##################################
##### Metadata Manipulations #####
##################################

def add_file_metadata(remote_filename, local_filename, timestamp_datetime, md5):
    _add(md5, {'remote_filename': remote_filename,
               'local_filename': local_filename,
               'timestamp_datetime': timestamp_datetime})


def get_file_metadata(md5):
    return _get(md5)


def get_latest_local_timestamp(remote_file_name):
    time_stamps = [i.get('timestamp_datetime', MIN_EPOCH_TIME)
                   for i in obj.values()
                   if i.get('remote_filename', '') == remote_file_name]

    if time_stamps:
        return max(time_stamps)
    else:
        return MIN_EPOCH_TIME


def print_inventory():
    print(str(obj))


###################################
###### Utils ######################
###################################

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

import ctypes
import os
import platform

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


def get_free_space_bytes(dir_name):
    """Return folder/drive free space (in bytes)."""
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dir_name), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(dir_name)
        return st.f_bavail * st.f_frsize

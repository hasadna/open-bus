import datetime
import hashlib
import os
from ftplib import FTP


def get_utc_time_underscored():
    """ return UTC time as underscored, to timestamp folders """
    t = datetime.datetime.utcnow()
    return t.strftime('%Y_%m_%d_%H_%M_%S')


def ftp_get_file(host, remote_path, local_path):
    """ get file remote_name from FTP host host and copied it inot local_path"""
    f = FTP(host)
    f.login()
    fh = open(local_path, 'wb')
    f.retrbinary('RETR %s' % (remote_path), fh.write)
    fh.close()
    f.quit()
    print("Retrieved from host %s: %s => %s" % (host, remote_path, local_path))


def md5_for_file(path, block_size=4096):
    """
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)
    """
    md5 = hashlib.md5()
    with open(path,'rb') as f: 
        for chunk in iter(lambda: f.read(block_size), b''): 
            md5.update(chunk)
    return md5.hexdigest()


def find_lastest_in_dir(dirname):
    def ctime_in_dirname(f):
        return os.path.getctime(os.path.join(dirname, f))
    
    if os.path.exists(dirname):
        files = os.listdir(dirname)
        if files:
            newest = max(os.listdir(dirname), key=ctime_in_dirname)
            return os.path.join(dirname,newest)
    return None

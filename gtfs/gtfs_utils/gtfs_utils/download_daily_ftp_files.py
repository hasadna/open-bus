import datetime
import os
import re
from .ftp import RE_FTP_LINE, get_ftp_dir, get_ftp_file

CONF = {
    'local_dir': 'C:\\dev\\ds\\open-bus-explore\\data\\archive\\',
    'size_limit': 1e7,
}


def get_files(local_dir=CONF['local_dir'], size_limit=CONF['size_limit']):
    files = [parsed['file_name'] for parsed in
             (re.search(RE_FTP_LINE, line) for line in get_ftp_dir())
             if parsed['size'] != '<DIR>'
             and int(parsed['size']) <= size_limit]

    daily_dir = local_dir + datetime.date.today().strftime('%Y-%m-%d') + '\\'

    try:
        os.mkdir(daily_dir)
    except FileExistsError:
        pass

    for file in files:
        get_ftp_file(file_name=file, local_path=daily_dir + file, force=True)


def main():
    get_files()


if __name__ == "__main__":
    main()

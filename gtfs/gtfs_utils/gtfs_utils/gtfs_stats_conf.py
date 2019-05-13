import re
from os.path import join, pardir

_base_folder_path = [pardir] * 4  # 4th parent dir
BASE_FOLDER = join(*_base_folder_path)

DATA_FOLDER = join(BASE_FOLDER, 'data')

ARCHIVE_FOLDER = join(DATA_FOLDER, 'archive')
LOCAL_TARIFF_PATH = join(ARCHIVE_FOLDER, '2019-03-17', 'Tariff.zip')


OUTPUT_FILE_NAME_RE = re.compile('^(?P<date_str>[^_]+?)'
                                 '_(?P<type>\w+)\.pkl\.gz')

BUCKET_NAME = 's3.obus.hasadna.org.il'
BUCKET_VALID_FILES_RE = re.compile('2019-\d\d-\d\d\.zip')
#BUCKET_VALID_FILES_RE = re.compile('2019-03-12.zip')

TATS_TYPES = ['trip_stats', 'route_stats']

import logging
import os
from datetime import datetime
from .configuration import configuration


def configure_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    datetime_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_name = f'gtfs_stats_{datetime_string}.log'
    log_file_full_path = os.path.join(configuration.files.full_paths.logs,
                                      log_file_name)
    file_handler = logging.FileHandler(log_file_full_path)

    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # add the handlers to the logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

"""
Script to download gtfs from MOT ftp and upload to S3 bucket.
To use the script create a config file. see example /conf/gtfs_download.config.example
Provide in command line args the path to config file
"""
import time
import os
import argparse
import tempfile
import datetime
import logging.config


import gtfs_retrieve_MOT_FTP
import gtfs_retrieve_S3
import gtfs_retrieve_FS
"""
 omerTODO - A general issue - I think the current md5 pickle is not a good method.
 First, if I understand correctly, the check is made against the whole history,
 but I think we only care about changes made to the latest file with the same name.
 For example, if one day they add a line to a file, the next day delete it,
 and on the third day they put it back in, we will be missing that third day file with no possibility to know.
 Second, what happens if the pickle gets corrupted?
    Aviv - We could add some of the file metadata such as date to the md5 calculation, similar to GIT:
        https://gist.github.com/masak/2415865 
"""
# omerTODO - use tempfile for EVERY download
# omerTODO - only save md5 of the LAST downloaded file (by type)
"""
Based on http://docs.python.org/howto/logging.html#configuring-logging
"""
# logging.config.fileConfig('logging.conf')
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger("default")

MOT_FTP = 'gtfs.mot.gov.il'


def download_file_and_upload_to_s3_bucket(connection, remote_file_name, no_md5):
    """ download remote file from mot ftp server, and upload to s3 Bucket """
    filename = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S_') + remote_file_name

    logger.info("Downloading '%s' to temp file..." % remote_file_name)
    file_path_temp = tempfile.NamedTemporaryFile(prefix=filename, delete=False)
    # closing file for now, will re-open when needed
    file_path_temp.close()
    file_path = file_path_temp.name

    gtfs_retrieve_MOT_FTP.ftp_get_file(file_path, MOT_FTP, remote_file_name)

    if not no_md5:
        tmp_md5 = gtfs_retrieve_FS.md5_for_file(file_path)
        try:
            # check if identical file already exists on AWS- retrieve current md5 of zip with same name
            last_md5 = connection.Object(filename).e_tag[1:-1]  # boto3 relives with ""
            if str(last_md5) == tmp_md5:
                logger.debug("Checksum's are identical - removing tmp file...")
                # remove tmp file
                os.unlink(file_path)
                return None
        except Exception:
            # file didn't exists
            pass

    logger.debug("The checksum for the latest file is different or the 'no_md5' flag is on -> uploading...")
    # upload to bucket
    gtfs_retrieve_S3.upload_file_to_s3_bucket(connection, file_path, filename)
    # remove tmp file
    os.unlink(file_path)


def print_dl_files_dict(dl_files_dict):
    for keys, values in dl_files_dict.items():
        logger.debug("md5 hash: " + keys)
        logger.debug("[remote_filename, local_filename, epoch in seconds]: %s", values)


def download_file(dest_dir, remote_file_name, no_timestamp, no_md5):
    gtfs_retrieve_FS.init(dest_dir)
    latest_local_timestamp = gtfs_retrieve_FS.get_latest_local_timestamp(remote_file_name)
    local_filename = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S_') + remote_file_name
    file_path = os.path.abspath(os.path.join(dest_dir, local_filename))
    if gtfs_retrieve_MOT_FTP.get_uptodateness(latest_local_timestamp, MOT_FTP, remote_file_name) or no_timestamp:
        logger.debug("New file have been found on '" + MOT_FTP + "' or the 'no_timestamp' flag is on")
        gtfs_retrieve_MOT_FTP.ftp_get_file(file_path, MOT_FTP, remote_file_name)
        file_md5 = gtfs_retrieve_FS.md5_for_file(file_path)
        # check if md5 already exists and add it if not
        if not (gtfs_retrieve_FS.get_file_metadata(file_md5)) or no_md5:
            gtfs_retrieve_FS.add_file_metadata(remote_file_name, local_filename, int(time.time()), file_md5)
            logger.debug("MD5 is different from previous downloads or the 'no_md5' flag is on")
        else:
            logger.debug(
                "The downloaded file '" + remote_file_name + "' already exists (according to md5 check), removing")
            os.remove(file_path)
    else:
        logger.debug("No newer (timestamp comparing) file have been found on FTP server skipping downloading")


def parse_cli_arguments():
    # parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(prog='MOT FTP server downloader and AWS S3 uploader')
    # if the option string is present but not followed by a command-line argument the value from const will be produced
    parser.add_argument("-d", dest='destination_directory', nargs='?', metavar='DIR_TO_DOWNLOAD',
                        help="download to local library (default=cwd)", const=os.getcwd())
    parser.add_argument("--no_timestamp", dest='no_timestamp', default=False, action='store_true',
                        help="skip timestamp comparing when downloading from ftp")
    parser.add_argument("--no_md5", dest='no_md5', default=False, action='store_true',
                        help="skip md5 comparing when downloading from ftp")
    parser.add_argument("--tempfile", dest='use_tempfile', action='store_true', default=False,
                        help="download to a tempfile for easier cleaning")
    parser.add_argument("-p", "--print", dest='print_inventory', nargs='?', metavar='DIR_OF_PICKLE_FILE',
                        help="print saved details about files name, hash and epoch time", const=os.getcwd())
    parser.add_argument("--print_ftp", action='store_true',
                        help="list all files on MOT's FTP")
    parser.add_argument("--aws", type=str, metavar='AWS_CONFIG_FILE', dest='aws_dl_ul', help="""upload current MOT FTP content to AWS S3 
        See /conf/gtfs_download.config.example for a template configuration file""")
    # nargs='*' - All command-line arguments present are gathered into a list
    parser.add_argument("--aws_ul", metavar=('AWS_CONFIG_FILE', 'PATH_OF_FILE_TO_UPLOAD'), type=str, dest='aws_ul',
                        help="""upload a file to AWS S3 
                                See /conf/gtfs_download.config.example for a template configuration file""",
                        nargs=2)
    parser.add_argument('--version', action='version', version='%(prog)s 3.1')
    return parser.parse_args()


def main():
    args = parse_cli_arguments()
    logger.debug("no_timestamp flag is %s", args.no_timestamp)
    logger.debug("no_md5 flag is %s", args.no_md5)

    if args.aws_dl_ul:
        logger.debug("option 'aws_dl_ul' was selected")
        files_on_ftp = gtfs_retrieve_MOT_FTP.get_ftp_files(MOT_FTP)
        for remote_file_name in files_on_ftp:
            connection = gtfs_retrieve_S3.connect_to_bucket(gtfs_retrieve_S3.parse_s3_config_file(args.aws_dl_ul))
            download_file_and_upload_to_s3_bucket(connection, remote_file_name, args.no_md5)

    if args.aws_ul:
        logger.debug("option 'aws_ul' was selected")
        local_file_to_upload = args.aws_ul[1]
        connection = gtfs_retrieve_S3.connect_to_bucket(gtfs_retrieve_S3.parse_s3_config_file(args.aws_ul[0]))
        gtfs_retrieve_S3.upload_file_to_s3_bucket(connection, local_file_to_upload, local_file_to_upload)

    if args.destination_directory:
        files_on_ftp = gtfs_retrieve_MOT_FTP.get_ftp_files(MOT_FTP)
        for remote_file_name in files_on_ftp:
            #if remote_file_name == 'israel-public-transportation.zip':
             #   continue
            download_file(args.destination_directory, remote_file_name, args.no_timestamp, args.no_md5)

    if args.print_inventory:
        gtfs_retrieve_FS.init(args.print_inventory)
        gtfs_retrieve_FS.print_inventory()

    if args.print_ftp:
        filenames_on_ftp = gtfs_retrieve_MOT_FTP.get_ftp_files(MOT_FTP)
        print(filenames_on_ftp)


if __name__ == '__main__':
    main()

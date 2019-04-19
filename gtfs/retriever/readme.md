## Download and Uploads Files



### Retrieve GTFS Files from MOT FTP
The folowing tool can be used to download GTFS files when new GTFS files are publish.

```
usage: gtfs_retrieve.py [-h] [-d [DIR_TO_DOWNLOAD]] [--no_timestamp]
                        [--no_md5] [--tempfile] [-p [DIR_OF_PICKLE_FILE]]
                        [--print_ftp] [--aws AWS_CONFIG_FILE]
                        [--aws_ul AWS_CONFIG_FILE PATH_OF_FILE_TO_UPLOAD]
                        [--version]

optional arguments:
  -h, --help            show this help message and exit
  -d [DIR_TO_DOWNLOAD]  download to local library (default=cwd)
  --no_timestamp        skip timestamp comparing when downloading from ftp
  --no_md5              skip md5 comparing when downloading from ftp
  --tempfile            download to a tempfile for easier cleaning
  -p [DIR_OF_PICKLE_FILE], --print [DIR_OF_PICKLE_FILE]
                        print saved details about files name, hash and epoch
                        time
  --print_ftp           list all files on MOT's FTP
  --aws AWS_CONFIG_FILE
                        upload current MOT FTP content to AWS S3 See
                        /conf/gtfs_download.config.example for a template
                        configuration file
  --aws_ul AWS_CONFIG_FILE PATH_OF_FILE_TO_UPLOAD
                        upload a file to AWS S3 See
                        /conf/gtfs_download.config.example for a template
                        configuration file
  --version             show program's version number and exit
```

### S3 Wrapper
The folowing tool can be used to Download, Upload, and List Files from open-bus S3 buckets. The tool have 3 commands:

**List Command**
```
usage: s3_wrapper.py list [-h] [--access-key-id <String>]
                          [--secret-access-key <String>]
                          [--bucket-name <String>] [--endpoint-url <String>]
                          [--access-preset ACCESS_PRESET]
                          [--prefix-filter <String>] [--regex-filter <String>]

optional arguments:
  -h, --help            show this help message and exit
  --access-key-id <String>, -aki <String>
                        access key id from S3 provider
  --secret-access-key <String>, -sak <String>
                        secret access key from S3 provider
  --bucket-name <String>, -bn <String>
                        bucket name in s3. (default: obus-do1)
  --endpoint-url <String>, -eu <String>
                        End point url of s3 service (in case of Amazon there
                        is no need to provide)
  --access-preset ACCESS_PRESET, -ap ACCESS_PRESET
                        use access preset default values: [aws / dig-private /
                        dig-public]
  --prefix-filter <String>, -pf <String>
                        filter files that their path starts with the given
                        string
  --regex-filter <String>, -rf <String>
                        filter files path by regex
```
**Download Command** 
```
usage: s3_wrapper.py download [-h] [--access-key-id <String>]
                              [--secret-access-key <String>]
                              [--bucket-name <String>]
                              [--endpoint-url <String>]
                              [--access-preset ACCESS_PRESET] --key <Path>
                              --local-file <Path>

optional arguments:
  -h, --help            show this help message and exit
  --access-key-id <String>, -aki <String>
                        access key id from S3 provider
  --secret-access-key <String>, -sak <String>
                        secret access key from S3 provider
  --bucket-name <String>, -bn <String>
                        bucket name in s3. (default: obus-do1)
  --endpoint-url <String>, -eu <String>
                        End point url of s3 service (in case of Amazon there
                        is no need to provide)
  --access-preset ACCESS_PRESET, -ap ACCESS_PRESET
                        use access preset default values: [aws / dig-private /
                        dig-public]
  --key <Path>, -k <Path>
                        key of a file in S3
  --local-file <Path>, -lf <Path>
                        reference for local file you wish to upload to path to
                        download to

```
**Upload Command** 

```
usage: s3_wrapper.py upload [-h] [--access-key-id <String>]
                            [--secret-access-key <String>]
                            [--bucket-name <String>] [--endpoint-url <String>]
                            [--access-preset ACCESS_PRESET] --key <Path>
                            --local-file <Path> [-fd] [--path-filter <String>]

optional arguments:
  -h, --help            show this help message and exit
  --access-key-id <String>, -aki <String>
                        access key id from S3 provider
  --secret-access-key <String>, -sak <String>
                        secret access key from S3 provider
  --bucket-name <String>, -bn <String>
                        bucket name in s3. (default: obus-do1)
  --endpoint-url <String>, -eu <String>
                        End point url of s3 service (in case of Amazon there
                        is no need to provide)
  --access-preset ACCESS_PRESET, -ap ACCESS_PRESET
                        use access preset default values: [aws / dig-private /
                        dig-public]
  --key <Path>, -k <Path>
                        key of a file in S3
  --local-file <Path>, -lf <Path>
                        reference for local file you wish to upload to path to
                        download to
  -fd, --folder         Add all files in a folder
  --path-filter <String>, -pf <String>
                        filter files path

```

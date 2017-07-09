
MOTS_URL=ftp://gtfs.mot.gov.il
FILE_NAME=israel-public-transportation.zip
GTFS_DATA_DIR=$1 
LOG_FILE=$2 
DATE=`date "+%Y%m%d"`
ARCHIVE_FILE=$GTFS_DATA_DIR/$DATE.zip

touch $LOG_FILE
touch $ARCHIVE_FILE

chmod +x $LOG_FILE
chmod +x $ARCHIVE_FILE

exec 3>&1 1>>${LOG_FILE} 2>&1

echo -e Getting zip file from $MOTS_URL to $ARCHIVE_FILE \n | tee /dev/fd/3
wget -O $ARCHIVE_FILE $MOTS_URL/$FILE_NAME
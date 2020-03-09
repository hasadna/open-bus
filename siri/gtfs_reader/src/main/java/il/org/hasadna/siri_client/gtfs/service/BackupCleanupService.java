package il.org.hasadna.siri_client.gtfs.service;

import il.org.hasadna.siri_client.gtfs.main.GtfsCollectorConfiguration;

import java.io.File;
import java.time.LocalDate;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class BackupCleanupService {

  private static Logger log = LoggerFactory.getLogger(BackupCleanupService.class);

  public void cleanup() {
    try {
      log.info("backup cleanup service started - checking expired backup files");

      for (String backupFilePrefix : GtfsCollectorConfiguration.getBackupFilesPrefixes()) {
        deleteExpiredBackupFiles(backupFilePrefix);
      }

      log.info("backup cleanup service done.");

    } catch (Exception e) {
      log.error("failed performing backup files cleanup", e);
    }
  }

  private void deleteExpiredBackupFiles(String filePrefix) {
    log.info("checking old backup files for prefix: '{}'", filePrefix);

    File gtfsRawFileBackupDirectory = new File(GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory());
    File[] fileInDirectory = gtfsRawFileBackupDirectory.listFiles();

    if (fileInDirectory == null) {
      log.info("no files found in backup files directory.");
      return;
    }

    for (File currentFile : fileInDirectory) {

      if (!currentFile.isDirectory() && currentFile.getName().startsWith(filePrefix)) {
        try {
          int startIndexOfDate = currentFile.getName().indexOf(filePrefix) + filePrefix.length();
          int finishIndexOfDate = startIndexOfDate + LocalDate.now().toString().length();

          LocalDate fileCreationDate = LocalDate.parse(currentFile.getName().substring(startIndexOfDate, finishIndexOfDate));

          if (isBackupFileExpired(fileCreationDate)) {
            log.info("file: {} is older than the configured time ({} days), removing file ", currentFile,
                    GtfsCollectorConfiguration.getGtfsBackupFilesStoreTimeInDays());

            if (!currentFile.delete()) {
              log.error("failed to remove file: " + currentFile);
            }
          }
        } catch (Exception e) {
          log.error("failed to handle possible expired file: " + currentFile.getName(), e);
        }
      }
    }
  }

  private boolean isBackupFileExpired(LocalDate fileCreationDate) {
    return fileCreationDate.isBefore(LocalDate.now().minusDays(GtfsCollectorConfiguration.getGtfsBackupFilesStoreTimeInDays()));
  }
}

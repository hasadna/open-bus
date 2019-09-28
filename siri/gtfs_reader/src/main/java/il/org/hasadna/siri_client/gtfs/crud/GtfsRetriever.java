package il.org.hasadna.siri_client.gtfs.crud;

import il.org.hasadna.siri_client.gtfs.main.GtfsCollectorConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class GtfsRetriever {

  private static final String GTFS_FTP_SERVER_HOST = "gtfs.mot.gov.il";
  private static final String GTFS_ZIP_FILE_NAME_ON_FTP = "israel-public-transportation.zip";
  private static final String MAKAT_FILE_NAME_ON_FTP = "TripIdToDate.zip";
  private static final String MAKAT_FILE_NAME_INSIDE_ZIP = "TripIdToDate.txt";
  public static final String ZIPPED_MAKAT_FILE_PREFIX = "makat";
  public static final String UNZIPPED_MAKAT_FILE_PREFIX = "TripIdToDate";
  public static final String GTFS_FILE_PREFIX = "gtfs";

  private static Logger logger = LoggerFactory.getLogger(GtfsRetriever.class);

  private FtpClientService ftpClientService;

  @Autowired
  public GtfsRetriever(FtpClientService ftpClientService) {
    this.ftpClientService = ftpClientService;
  }

  public Path retrieverGtfsFile() throws IOException {
    try {
      logger.info("downloading gtfs file from ftp");

      Path gtfsZipOutputPath = Paths.get(generateFileNameWithDate(GTFS_FILE_PREFIX, ".zip"));

      ftpClientService.downloadFileWithRetry(GTFS_FTP_SERVER_HOST, GTFS_ZIP_FILE_NAME_ON_FTP, gtfsZipOutputPath);

      logger.info("done downloading gtfs file from ftp");

      return gtfsZipOutputPath;

    } catch (DownloadFailedException ex) {
      // use an older file
      logger.info("handling DownloadFailedException, search older gtfs files...");
      Path olderGtfs = findOlderGtfsFile();
      if (olderGtfs != null) {
        logger.info("using newest older gtfs file {}", olderGtfs.getFileName());
      } else {
        logger.info("older gtfs files were not found!");
      }
      return olderGtfs;
    }
  }

  public static Path findOlderGtfsFile() throws IOException {
    File gtfsPath = new File(GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory());

    if (!gtfsPath.isDirectory()) {
      throw new DownloadFailedException("can't find directory: "
          + GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory());
    }

    File[] x = gtfsPath.listFiles();
    logger.trace("all files: [{}]", Arrays.stream(x).map(File::getName).collect(Collectors.joining(",")));
    List<File> allGtfsFiles =
        Arrays.stream(x).
            filter(file -> !file.isDirectory() && file.getName().startsWith(GTFS_FILE_PREFIX) && file.getName().endsWith("zip")).
            sorted(File::compareTo).
            collect(Collectors.toList());

    if (allGtfsFiles.isEmpty()) {
      return null;
    }

    Collections.reverse(allGtfsFiles);  // reverse so we get the newest file first

    logger.info("all gtfs files: [{}]", allGtfsFiles.stream().map(File::getName).collect(Collectors.joining(",")));
    File newestGtfs = allGtfsFiles.stream().findFirst().get();

    logger.info("newest gtfs file: {}", newestGtfs.getName());
    return Paths.get(newestGtfs.getAbsolutePath());
  }



  public Path retrieveMakatFile() throws IOException {
    logger.info("downloading makat file");
    Path makatZipOutputPath = Paths.get(generateFileNameWithDate(ZIPPED_MAKAT_FILE_PREFIX, ".zip"));
    Path makatFile = ftpClientService.downloadFileWithRetry(GTFS_FTP_SERVER_HOST, MAKAT_FILE_NAME_ON_FTP, makatZipOutputPath);
    logger.info("makat file downloaded as {}", makatFile);

    logger.info("unzipping makat file");
    GtfsZipFile makatZipFile = new GtfsZipFile(makatFile);
    Path makatExtractedOutputPath = Paths.get(generateFileNameWithDate(UNZIPPED_MAKAT_FILE_PREFIX, ".txt"));

    makatZipFile.extractFile(MAKAT_FILE_NAME_INSIDE_ZIP, makatExtractedOutputPath);
    logger.info("unzipped makat file to {}", makatExtractedOutputPath);

    return makatExtractedOutputPath;
  }

  private String generateFileNameWithDate(String filePrefix, String fileSuffix) {
    return GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory() + filePrefix + LocalDate.now().toString() + fileSuffix;
  }
}

package il.org.hasadna.siri_client.gtfs.crud;

import java.io.*;
import java.net.ConnectException;
import java.net.SocketTimeoutException;
import java.nio.file.*;
import java.nio.file.attribute.FileAttribute;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import net.jodah.failsafe.Failsafe;
import net.jodah.failsafe.RetryPolicy;
import org.apache.commons.net.ftp.FTP;
import org.apache.commons.net.ftp.FTPClient;
import org.apache.commons.net.ftp.FTPReply;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class GtfsFtp {

  private static final String HOST = "gtfs.mot.gov.il";
  private static final String FILE_NAME = "israel-public-transportation.zip";
  private static final String MAKAT_FILE_NAME_ON_FTP = "TripIdToDate.zip";
  private static final String TEMP_DIR = "/tmp/";

  private static Logger logger = LoggerFactory.getLogger(GtfsFtp.class);

  FTPClient connect(String host) throws IOException {
    FTPClient ftpClient = createFTPClient();
    try {
      if (System.getProperty("gtfs.connect.timeout") != null) {
        int timeout = Integer.parseInt(System.getProperty("gtfs.connect.timeout"));
        ftpClient.setConnectTimeout(timeout);    // milliseconds
      } }
    catch (Exception ex) {
      // absorb on purpose, timeout will remain as it was
      logger.warn("absorbing exception while parsing value of system property gtfs.connect.timeout", ex);
    }
    ftpClient.connect(host);
    ftpClient.login("anonymous", "");
    ftpClient.enterLocalPassiveMode();
    ftpClient.setFileType(FTP.BINARY_FILE_TYPE);
    if (!FTPReply.isPositiveCompletion(ftpClient.getReplyCode())) {
      throw new IOException("Faild to connect to: " + host);
    }
    return ftpClient;
  }

  public Path downloadGtfsZipFile() throws IOException {
    try {
      return downloadGtfsZipFile(createTempFile("gtfs"));
    }
    catch (DownloadFailedException ex) {
      // use an older file
      logger.info("handling DownloadFailedException, search older gtfs files...");
      Path olderGtfs = findOlderGtfsFile(LocalDate.now());
      if (olderGtfs != null) {
        logger.info("using newest older gtfs file {}", olderGtfs.getFileName());
      }
      else {
        logger.info("older gtfs files were not found!");
      }
      return olderGtfs;
    }
  }

  public static Path findOlderGtfsFile(LocalDate now) throws IOException {
    File dir = new File(TEMP_DIR);
    if (!dir.isDirectory()) {
      throw new DownloadFailedException("can't find directory " + TEMP_DIR);
    }
    File[] x = dir.listFiles();
    logger.trace("all files: [{}]", Arrays.stream(x).map(file -> file.getName()).collect(Collectors.joining(",")));
    List<File> allGtfsFiles =
        Arrays.asList(x).stream().
            filter(file -> !file.isDirectory() && file.getName().startsWith("gtfs") && file.getName().endsWith("zip")).
            sorted(File::compareTo).
            collect(Collectors.toList());
    if (allGtfsFiles.isEmpty()) return null;
    Collections.reverse(allGtfsFiles);  // reverse so we get the newest file first
    logger.info("all gtfs files: [{}]", allGtfsFiles.stream().map(file -> file.getName()).collect(Collectors.joining(",")));
    File newestGtfs = allGtfsFiles.stream().
        findFirst().get();
//                orElseThrow(() -> new DownloadFailedException("can't find older gtfs files in " + TEMP_DIR));
    logger.info("newest gtfs file: {}", newestGtfs.getName());
    return Paths.get(newestGtfs.getAbsolutePath());
  }

  Path createTempFile(String prefix) throws IOException {
    return Files.createTempFile(prefix, null);
  }

  public Path downloadMakatZipFile() throws IOException {
    logger.info("downloading makat file");
    Path makatFile = downloadMakatZipFile(createTempFile("makat"));
    logger.info("makat file downloaded as {}", makatFile);

    logger.info("unzipping makat file");
    GtfsZipFile makatZipFile = new GtfsZipFile(makatFile);
    Path unzippedMakatTempFile = makatZipFile.extractFile("TripIdToDate.txt", "makat" + LocalDate.now().toString());
    logger.info("unzipped makat file to {}", unzippedMakatTempFile);
    Path unzippedMakatFile = renameFile(unzippedMakatTempFile, "TripIdToDate", ".txt");
    logger.info("renamed unzipped makat file to {}", unzippedMakatFile);
    return unzippedMakatFile;
  }

  private Path downloadMakatZipFile(final Path pathIn) throws IOException {
    try {
      // download makat file. If download fails, will retry up to 5 retries
      RetryPolicy retryPolicy = new RetryPolicy()
          .retryOn(DownloadFailedException.class)
          .withBackoff(1, 30 , TimeUnit.MINUTES)
          .withMaxRetries(5);

      Path path = Failsafe.with(retryPolicy).get(() -> downloadFile(pathIn, MAKAT_FILE_NAME_ON_FTP));

      logger.info("renaming makat file...");
      Path newPath = renameMakatFile(path);
      logger.info("                  ...done");
      return newPath;
    }
    finally {
    }
  }

  private Path downloadGtfsZipFile(final Path pathIn) throws IOException {
    try {
      Path path = downloadFile(pathIn, FILE_NAME);

      logger.info("renaming gtfs file...");
      Path newPath = renameGtfsFile(path);
      logger.info("                  ...done");
      return newPath;
    }
    finally {
    }
  }



  private Path downloadFile(Path path, String FILE_NAME) throws IOException {
    OutputStream out = null ;
    try {
      try {
        logger.info("connect to ftp...");
        FTPClient conn = connect(HOST);
        out = new BufferedOutputStream(new FileOutputStream(path.toFile()));

        logger.info("start downloading from ftp...");

        if (!conn.retrieveFile(FILE_NAME, out)) {
          logger.error("retrieveFile returned false, fileName={}", FILE_NAME);
          throw new DownloadFailedException("Failed to download the file: " + FILE_NAME);
        }
      }
      catch (ConnectException ex) {
        logger.error("failed to retrieve file from ftp", ex);
        throw new DownloadFailedException("Failed to download the file: " + FILE_NAME);
      }
      catch (SocketTimeoutException ex) {
        logger.error("failed to retrieve file from ftp", ex);
        throw new DownloadFailedException("Failed to download the file: " + FILE_NAME);
      }
      catch (IOException ex) {
        logger.error("failed to retrieve file from ftp", ex);
        throw new DownloadFailedException("Failed to download the file: " + FILE_NAME);
      }
      out.close();
      logger.info("                          ... done");

      return path;
    }
    finally {
      if (out != null) {
        out.close();
      }
    }
  }

  private Path renameMakatFile(final Path path) {
    return renameFile(path, "TripIdToDate");
  }

  private Path renameGtfsFile(final Path path) {
    return renameFile(path, "gtfs");
  }

  private Path renameFile(final Path path, final String prefix) {
    return renameFile(path, prefix, ".zip");
  }
  private Path renameFile(final Path path, final String prefix, final String suffix) {
    try {
      String meaningfulName = TEMP_DIR + prefix + LocalDate.now().toString() + suffix;
      Path newName = Paths.get(meaningfulName);
      Path newPath = Files.move(path, newName, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
      logger.trace("file renamed to {}", newPath);
      return newPath;
    }
    catch (IOException ex) {
      logger.error("failed to rename file, stay with original name", ex);
      return path;
    }
  }

  FTPClient createFTPClient() {
    return new FTPClient();
  }

}

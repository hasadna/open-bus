package il.org.hasadna.siri_client.gtfs.crud;

import il.org.hasadna.siri_client.gtfs.main.GtfsCollectorConfiguration;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.ConnectException;
import java.net.SocketTimeoutException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
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

	private static Logger logger = LoggerFactory.getLogger(GtfsFtp.class);

	FTPClient connect(String host) throws IOException {
		FTPClient ftpClient = createFTPClient();
		try {
		if (System.getProperty("gtfs.connect.timeout") != null) {
		    int timeout = Integer.parseInt(System.getProperty("gtfs.connect.timeout"));
            ftpClient.setConnectTimeout(timeout);    // seconds
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
    return downloadGtfsZipFile(getGtfsZipFilePath());
	}

    public static Optional<Path> findOlderGtfsFile(LocalDate now) throws IOException {
	    File dir = new File(GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory());
	    if (!dir.isDirectory()) {
	        throw new DownloadFailedException("can't find directory " + GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory());
        }
        File[] x = dir.listFiles();
	    logger.trace("all files: [{}]", Arrays.stream(x).map(file -> file.getName()).collect(Collectors.joining(",")));
	    List<File> allGtfsFiles =
            Arrays.asList(x).stream().
                filter(file -> !file.isDirectory() && file.getName().startsWith("gtfs")).
                sorted(File::compareTo).
                collect(Collectors.toList());
        Collections.reverse(allGtfsFiles);  // reverse so we get the newest file first
        logger.info("all gtfs files: [{}]", allGtfsFiles.stream().map(file -> file.getName()).collect(Collectors.joining(",")));

        if (allGtfsFiles.isEmpty()) {
          logger.info("couldn't find any older gtfs file in: {}", GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory());
          return Optional.empty();
        }

        File newestGtfs = allGtfsFiles.get(0);

        logger.info("newest gtfs file: {}", newestGtfs.getName());

        return Optional.of(Paths.get(newestGtfs.getAbsolutePath()));
    }

    Path getGtfsZipFilePath() throws IOException {

		return Files.createTempFile(Paths.get(GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory()),
        null, null, PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-rw-rw-")));
	}


    public Path downloadMakatZipFile() throws IOException {
      final Path tempPath = Paths.get(GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory() + "/" + "makat-" + LocalDate.now().toString() + ".zip");
      Path path = downloadFile(tempPath);
      return path;
    }

    private Path downloadFile(Path path) throws IOException {
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

	private Path downloadGtfsZipFile(final Path pathIn) throws IOException {
    Path path = downloadFile(pathIn);

    logger.info("renaming gtfs file...");
    Path newPath = renameGtfsFile(path);
    logger.info("                  ...done");

    return newPath;
	}

    private Path renameGtfsFile(final Path path) {
	    try {
            String meaningfulName = GtfsCollectorConfiguration.getGtfsRawFilesBackupDirectory() + "gtfs" + LocalDate.now().toString() + ".zip";
            Path newName = Paths.get(meaningfulName);
            logger.info("moving gtfs zip file from: {} to {}", path, newName);
            Path newPath = Files.move(path, newName, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
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

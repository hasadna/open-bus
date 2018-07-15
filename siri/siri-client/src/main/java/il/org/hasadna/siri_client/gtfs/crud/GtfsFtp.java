package il.org.hasadna.siri_client.gtfs.crud;

import java.io.*;
import java.net.ConnectException;
import java.net.SocketTimeoutException;
import java.nio.file.*;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import il.org.hasadna.siri_client.gtfs.main.DefaultGtfsQueryBasedOnFtp;
import org.apache.commons.net.ftp.FTP;
import org.apache.commons.net.ftp.FTPClient;
import org.apache.commons.net.ftp.FTPReply;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GtfsFtp {

	private static final String HOST = "gtfs.mot.gov.il";
	private static final String FILE_NAME = "israel-public-transportation.zip";
    private static final String TEMP_DIR = "/tmp/";

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
	    try {
            return downloadGtfsZipFile(createTempFile());
        }
        catch (DownloadFailedException ex) {
	        // use an older file
            logger.info("handling DownloadFailedException, search older gtfs files...");
	        Path olderGtfs = findOlderGtfsFile(LocalDate.now());
	        logger.info("using newest older gtfs file {}", olderGtfs.getFileName());
	        return olderGtfs;
        }
	}

    private Path findOlderGtfsFile(LocalDate now) throws IOException {
	    File dir = new File(TEMP_DIR);
	    if (!dir.isDirectory()) {
	        throw new DownloadFailedException("can't find directory " + TEMP_DIR);
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
        File newestGtfs = allGtfsFiles.stream().
                findFirst().
                orElseThrow(() -> new DownloadFailedException("can't find older gtfs files in " + TEMP_DIR));
        logger.info("newest gtfs file: {}", newestGtfs.getName());
        return Paths.get(newestGtfs.getAbsolutePath());
    }

    Path createTempFile() throws IOException {

		return Files.createTempFile(null, null);
	}

	private Path downloadGtfsZipFile(Path path) throws IOException {
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
                logger.error("failed to retrieve GTFS file from ftp", ex);
                throw new DownloadFailedException("Failed to download the file: " + FILE_NAME);
            }
            catch (SocketTimeoutException ex) {
                logger.error("failed to retrieve GTFS file from ftp", ex);
                throw new DownloadFailedException("Failed to download the file: " + FILE_NAME);
            }
            out.close();
            logger.info("                          ... done");

            logger.info("renaming gtfs file...");
            Path newPath = renameFile(path);
            logger.info("                  ...done");
            return  newPath;
        }
        finally {
	        if (out != null) {
                out.close();
            }
        }
	}

    private Path renameFile(final Path path) {
	    try {
            String meaningfulName = TEMP_DIR + "gtfs" + LocalDate.now().toString() + ".zip";
            Path newName = Paths.get(meaningfulName);
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

	private class DownloadFailedException extends IOException {
	    public DownloadFailedException() {
	        super();
        }
        public DownloadFailedException(String message) {
	        super(message);
        }
        public DownloadFailedException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}

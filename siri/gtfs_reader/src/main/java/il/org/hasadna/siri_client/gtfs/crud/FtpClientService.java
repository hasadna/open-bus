package il.org.hasadna.siri_client.gtfs.crud;

import il.org.hasadna.siri_client.gtfs.main.GtfsCollectorConfiguration;
import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import net.jodah.failsafe.Failsafe;
import net.jodah.failsafe.RetryPolicy;
import org.apache.commons.net.ftp.FTP;
import org.apache.commons.net.ftp.FTPClient;
import org.apache.commons.net.ftp.FTPReply;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class FtpClientService {

  private static Logger logger = LoggerFactory.getLogger(FtpClientService.class);

  public Path downloadFileWithRetry(String ftpServer, String remoteFileName, Path localFilePath) throws DownloadFailedException {

    try {
      RetryPolicy retryPolicy = new RetryPolicy()
          .retryOn(DownloadFailedException.class)
          .withBackoff(1, 30, TimeUnit.MINUTES)
          .withMaxRetries(5);

      return Failsafe.with(retryPolicy).get(() -> downloadFile(ftpServer, remoteFileName, localFilePath));

    } catch (Exception e) {
      throw new DownloadFailedException(e);
    }
  }

  private Path downloadFile(String ftpServer, String remoteFileName, Path localFilePath) throws DownloadFailedException {
    OutputStream localFileOutputStream = null;

    try {
      logger.info("connect to ftp...");
      FTPClient ftpClient = connect(ftpServer);
      localFileOutputStream = new BufferedOutputStream(new FileOutputStream(localFilePath.toFile()));

      logger.info("start downloading from ftp...");

      if (!ftpClient.retrieveFile(remoteFileName, localFileOutputStream)) {
        logger.error("retrieveFile returned false, fileName={}", remoteFileName);
        throw new DownloadFailedException("Failed to download the file: " + remoteFileName);
      }

      return localFilePath;

    } catch (IOException ex) {
      logger.error("failed to retrieve file from ftp", ex);
      throw new DownloadFailedException("Failed to download the file: " + remoteFileName);

    } finally {
      logger.info("                          ... done");

      if (localFileOutputStream != null) {
        try {
          localFileOutputStream.close();
        } catch (IOException e) {
          logger.error("failed to close local file output stream", e);
        }
      }
    }

  }

  private FTPClient connect(String host) throws IOException {
    FTPClient ftpClient = new FTPClient();
    ftpClient.setConnectTimeout((int)GtfsCollectorConfiguration.getGtfsConnectTimeoutMilliseconds());
    ftpClient.connect(host);
    ftpClient.login("anonymous", "");
    ftpClient.enterLocalPassiveMode();
    ftpClient.setFileType(FTP.BINARY_FILE_TYPE);

    if (!FTPReply.isPositiveCompletion(ftpClient.getReplyCode())) {
      throw new IOException("Faild to connect to: " + host);
    }

    return ftpClient;
  }

}

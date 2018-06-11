package il.org.hasadna.siri_client.gtfs.ftp;

import java.io.IOException;
import java.net.InetAddress;
import java.net.SocketException;
import java.util.NoSuchElementException;
import java.util.stream.Stream;

import org.apache.commons.net.ftp.FTPClient;
import org.apache.commons.net.ftp.FTPFile;
import org.apache.commons.net.ftp.FTPReply;

public class MotFTP {

	private static final String FTP_HOST_NAME = "gtfs.mot.gov.il";

	public MotFTP() {

	}

	public FTPFile getFTPFile() throws SocketException, IOException {
		FTPClient ftpClient = connectToFtp(FTP_HOST_NAME);
		return Stream.of(ftpClient.listFiles())
				.filter(i -> i.getName().equals("israel-public-transportation.zip"))
				.findAny().orElseThrow(() -> new NoSuchElementException());
	}

	static FTPClient connectToFtp(String ftpHostName) throws SocketException, IOException {
		FTPClient ftpClient = new FTPClient();
		ftpClient.connect(ftpHostName);

		if (!FTPReply.isPositiveCompletion(ftpClient.getReplyCode())) {
			throw new IOException("can not connect to server " + ftpHostName);
		}

		return ftpClient;
	}

}

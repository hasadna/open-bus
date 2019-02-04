package il.org.hasadna.siri_client.gtfs.crud;

import static org.junit.Assert.*;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.OutputStream;
import java.net.SocketException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.apache.commons.net.ftp.FTPClient;
import org.junit.Test;

import il.org.hasadna.siri_client.gtfs.crud.GtfsFtp;

public class GtfsFtpTest {

	@Test
	public void testConnect() throws IOException {
		GtfsFtp gtfsFtp = new GtfsFtp() {
			@Override
			protected FTPClient createFTPClient() {

				return new FTPClient() {
					@Override
					public void connect(String hostname) throws SocketException, IOException {

					}

					@Override
					public boolean login(String username, String password) throws IOException {

						return true;
					}

					@Override
					public boolean setFileType(int fileType) throws IOException {

						return true;
					}

					@Override
					public int getReplyCode() {
						return 220;
					}
				};
			}
		};
		FTPClient actual = gtfsFtp.connect("localhost");
		int replyCode = actual.getReplyCode();

		assertEquals(220, replyCode);
	}

	@Test(expected = IOException.class)
	public void testConnect_with_negativ_return_code() throws IOException {
		GtfsFtp gtfsFtp = new GtfsFtp() {
			@Override
			protected FTPClient createFTPClient() {

				return new FTPClient() {
					@Override
					public void connect(String hostname) throws SocketException, IOException {

					}

					@Override
					public boolean login(String username, String password) throws IOException {

						return true;
					}

					@Override
					public boolean setFileType(int fileType) throws IOException {

						return true;
					}

					@Override
					public int getReplyCode() {
						return 301;
					}
				};
			}
		};
		gtfsFtp.connect("localhost");
	}

	@Test(expected = IOException.class)
	public void testConnect_with_login_exception() throws IOException {
		GtfsFtp gtfsFtp = new GtfsFtp() {
			@Override
			protected FTPClient createFTPClient() {

				return new FTPClient() {
					@Override
					public void connect(String hostname) throws SocketException, IOException {

					}

					@Override
					public boolean login(String username, String password) throws IOException {

						throw new IOException();
					}
				};
			}
		};
		gtfsFtp.connect("localhost");
	}

	@Test
	public void testCreateFTPClient() {
		GtfsFtp gtfsFtp = new GtfsFtp();
		FTPClient actual = gtfsFtp.createFTPClient();
		assertNotNull(actual);
	}

	@Test
	public void testDownloadGtfsZipFile() throws IOException {

		Path expected = Files.createTempFile(null, null);

		GtfsFtp gtfsFtp = new GtfsFtp() {
			@Override
			Path createTempFile(String prefix) throws IOException {
				return expected;
			}

			@Override
			FTPClient connect(String host) throws IOException {

				return new FTPClient() {
					@Override
					public boolean retrieveFile(String remote, OutputStream local) throws IOException {
						return true;
					}
				};
			}
		};

		Path actual = gtfsFtp.downloadGtfsZipFile();

		assertEquals(expected, actual);
	}

	@Test(expected = FileNotFoundException.class)
	public void testDownloadGtfsZipFile_not_exist_target_path() throws IOException {

		Path expected = Paths.get("non/exist/file.c");

		GtfsFtp gtfsFtp = new GtfsFtp() {
			@Override
			Path createTempFile(String prefix) throws IOException {
				return expected;
			}

			@Override
			FTPClient connect(String host) throws IOException {

				return new FTPClient() {

				};
			}

		};

		gtfsFtp.downloadGtfsZipFile();

	}

	@Test(expected = IOException.class)
	public void testDownloadGtfsZipFile_failed_to_download() throws IOException {

		GtfsFtp gtfsFtp = new GtfsFtp() {

			@Override
			FTPClient connect(String host) throws IOException {

				return new FTPClient() {
					@Override
					public boolean retrieveFile(String remote, OutputStream local) throws IOException {
						return false;
					}
				};
			}

		};

		gtfsFtp.downloadGtfsZipFile();

	}
}

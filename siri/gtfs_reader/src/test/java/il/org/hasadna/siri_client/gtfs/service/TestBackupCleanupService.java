package il.org.hasadna.siri_client.gtfs.service;

import il.org.hasadna.siri_client.gtfs.main.GtfsCollectorConfiguration;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.LocalDate;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.junit.MockitoJUnitRunner;

@RunWith(MockitoJUnitRunner.class)
public class TestBackupCleanupService {


  private BackupCleanupService backupCleanupService;

  @Before
  public void setUp() {
    backupCleanupService = new BackupCleanupService();
  }

  @Test
  public void testCleanup_BackupDirectoryIsNotExist() {
    // given
    new GtfsCollectorConfiguration().setGtfsRawFilesBackupDirectory("/unit-test");
    new GtfsCollectorConfiguration().setBackupFilesPrefixes("");

    // when
    backupCleanupService.cleanup();

    // then
  }

  @Test
  public void testCleanup_DirectoryHasFile_NotExpired() throws IOException {
    // given
    Path tempDirectory = Files.createTempDirectory("unit_test", PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwxrwxrwx")));

    Path backupFile = Files.createFile(Paths.get(tempDirectory + "/prefix" + LocalDate.now().toString()),
        PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-rw-rw-")));

    new GtfsCollectorConfiguration().setGtfsRawFilesBackupDirectory(tempDirectory.toAbsolutePath().toString());
    new GtfsCollectorConfiguration().setBackupFilesPrefixes("[prefix]");

    // when
    backupCleanupService.cleanup();

    // then
    Assert.assertTrue("back up file shouldn't removed", backupFile.toFile().exists());
    tempDirectory.toFile().delete();
  }

  @Test
  public void testCleanup_DirectoryHasFile_FileExpired() throws IOException {
    // given
    Path tempDirectory = Files.createTempDirectory("unit_test", PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwxrwxrwx")));

    new GtfsCollectorConfiguration().setGtfsBackupFilesStoreTimeInDays("1");
    Path backupFile = Files.createFile(Paths.get(tempDirectory + "/prefix" + LocalDate.now().minusDays(5).toString()),
        PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-rw-rw-")));

    new GtfsCollectorConfiguration().setGtfsRawFilesBackupDirectory(tempDirectory.toAbsolutePath().toString());
    new GtfsCollectorConfiguration().setBackupFilesPrefixes("[prefix]");

    // when
    backupCleanupService.cleanup();

    // then
    Assert.assertFalse("back up file should be removed", backupFile.toFile().exists());
    tempDirectory.toFile().delete();
  }


  @Test
  public void testCleanup_DirectoryHasFile_FileExpired_DirectoryHasInvalidFiles() throws IOException {
    // given
    Path tempDirectory = Files.createTempDirectory("unit_test", PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwxrwxrwx")));

    new GtfsCollectorConfiguration().setGtfsBackupFilesStoreTimeInDays("1");
    Path backupFile = Files.createFile(Paths.get(tempDirectory + "/prefix" + LocalDate.now().minusDays(5).toString()),
            PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-rw-rw-")));

    Path invalidBackupFile = Files.createFile(Paths.get(tempDirectory + "/prefix" + "invalid-date"),
            PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-rw-rw-")));


    new GtfsCollectorConfiguration().setGtfsRawFilesBackupDirectory(tempDirectory.toAbsolutePath().toString());
    new GtfsCollectorConfiguration().setBackupFilesPrefixes("[prefix]");

    // when
    backupCleanupService.cleanup();

    // then
    Assert.assertFalse("back up file should be removed", backupFile.toFile().exists());
    Assert.assertTrue("file with invalid date shouldn't be removed", invalidBackupFile.toFile().exists());
    tempDirectory.toFile().delete();
  }

  @Test
  public void testCleanup_DirectoryHasMultipleFiles_SomeExpired_SomeNotExpired() throws IOException {
    // given
    Path tempDirectory = Files.createTempDirectory("unit_test", PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwxrwxrwx")));

    new GtfsCollectorConfiguration().setGtfsBackupFilesStoreTimeInDays("1");

    Path expiredBackupFile1 = Files.createFile(Paths.get(tempDirectory + "/prefix1" + LocalDate.now().minusDays(5).toString()),
        PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-rw-rw-")));

    Path notExpiredBackupFile1 = Files.createFile(Paths.get(tempDirectory + "/prefix1" + LocalDate.now().toString()),
        PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-rw-rw-")));

    Path expiredBackupFile2 = Files.createFile(Paths.get(tempDirectory + "/prefix2" + LocalDate.now().minusDays(5).toString()),
        PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-rw-rw-")));

    Path notExpiredBackupFile2 = Files.createFile(Paths.get(tempDirectory + "/prefix2" + LocalDate.now().toString()),
        PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-rw-rw-")));

    new GtfsCollectorConfiguration().setGtfsRawFilesBackupDirectory(tempDirectory.toAbsolutePath().toString());
    new GtfsCollectorConfiguration().setBackupFilesPrefixes("[prefix1,prefix2]");

    // when
    backupCleanupService.cleanup();

    // then
    Assert.assertFalse("expired back up file should be removed", expiredBackupFile1.toFile().exists());
    Assert.assertTrue("not expired back up file shouldn't be removed", notExpiredBackupFile1.toFile().exists());

    Assert.assertFalse("expired back up file should be removed", expiredBackupFile2.toFile().exists());
    Assert.assertTrue("not expired back up file shouldn't be removed", notExpiredBackupFile2.toFile().exists());

    tempDirectory.toFile().delete();
  }
}
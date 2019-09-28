package il.org.hasadna.siri_client.gtfs.main;

import static il.org.hasadna.siri_client.gtfs.crud.GtfsRetriever.GTFS_FILE_PREFIX;
import static il.org.hasadna.siri_client.gtfs.crud.GtfsRetriever.UNZIPPED_MAKAT_FILE_PREFIX;
import static il.org.hasadna.siri_client.gtfs.crud.GtfsRetriever.ZIPPED_MAKAT_FILE_PREFIX;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class GtfsCollectorConfiguration {

    private static final int DEFAULT_BACKUP_FILES_STORE_TIME_IN_DAYS = 5;
    private final LocalTime DEFAULT_WHEN_TO_DOWNLOAD = LocalTime.of(3, 30);
    private final LocalDate DEFAULT_DATE_OF_LAST_DOWNLOAD = LocalDate.of(2000, 1, 1);
    private final long DEFAULT_SECONDS_BETWEEN_CHECKS_IN_MILLISECONDS = TimeUnit.MINUTES.toMillis(15);
    private final String DEFAULT_RESCHEDULE_URL = "http://localhost:8080/data/schedules/read/all";
    private final List<String> DEFAULT_LIST_OF_AGENCIES = Collections.singletonList("5");
    private final List<String> DEFAULT_LIST_OF_BACKUP_FILE_PREFIXES = Arrays.asList(GTFS_FILE_PREFIX, ZIPPED_MAKAT_FILE_PREFIX, UNZIPPED_MAKAT_FILE_PREFIX);

    private static Boolean downloadTodaysFile = true;
    private static Boolean gtfsDownloadDisabled = false;
    private static LocalTime whenToDownload;
    private static LocalDate dateOfLastDownload;
    private static long millisecondsBetweenGtfsChecks;
    private static String schedulesLocation;
    private static String rescheduleUrl;
    private static List<String> agencies;
    private static List<String> backupFilesPrefixes;
    private static String gtfsRawFilesBackupDirectory;
    private static long gtfsConnectTimeoutMilliseconds = 10000;
    private static int gtfsBackupFilesStoreTimeInDays = 5;

    public static long getGtfsConnectTimeoutMilliseconds() {
        return gtfsConnectTimeoutMilliseconds;
    }

    @Value("${gtfs.connect.timeout.milliseconds:10000}")
    public void setGtfsConnectTimeoutMilliseconds(long gtfsConnectTimeoutMilliseconds) {
        GtfsCollectorConfiguration.gtfsConnectTimeoutMilliseconds = gtfsConnectTimeoutMilliseconds;
    }

    public static String getGtfsRawFilesBackupDirectory() {
        return gtfsRawFilesBackupDirectory;
    }

    @Value("${gtfs.RawFilesBackupDirectory:/tmp/}")
    public void setGtfsRawFilesBackupDirectory(String gtfsRawFilesBackupDirectory) {
        if (!gtfsRawFilesBackupDirectory.endsWith("/")) {
            gtfsRawFilesBackupDirectory += "/";
        }

        GtfsCollectorConfiguration.gtfsRawFilesBackupDirectory = gtfsRawFilesBackupDirectory;
    }

    @Value("${gtfs.gtfsDownloadDisabled:false}")
    public void setDisableDownload(Boolean disableDownload) {
        GtfsCollectorConfiguration.gtfsDownloadDisabled = disableDownload;
    }

    public static Boolean getGtfsDownloadDisabled() {
        return gtfsDownloadDisabled;
    }

    public Boolean getDownloadTodaysFile() {
        return downloadTodaysFile;
    }

    @Value("${gtfs.downloadToday:true}")
    public void setDownloadTodaysFile(Boolean downloadTodaysFile) {
        GtfsCollectorConfiguration.downloadTodaysFile = downloadTodaysFile;
    }

    public static LocalTime getWhenToDownload() {
        return whenToDownload;
    }

    @Value("${gtfs.whenToDownload:}")
    public void setWhenToDownload(String whenToDownload) {
        if (!whenToDownload.isEmpty()) {
            GtfsCollectorConfiguration.whenToDownload = LocalTime.parse(whenToDownload, DateTimeFormatter.ofPattern("HH:mm"));
        } else {
            GtfsCollectorConfiguration.whenToDownload = DEFAULT_WHEN_TO_DOWNLOAD;
        }

    }

    public static LocalDate getDateOfLastDownload() {
        return dateOfLastDownload;
    }

    @Value("${gtfs.dateOfLastDownload:}")
    public void setDateOfLastDownload(String dateOfLastDownload) {
        if (!dateOfLastDownload.isEmpty()) {
            GtfsCollectorConfiguration.dateOfLastDownload = LocalDate.parse( dateOfLastDownload , DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        } else {
            GtfsCollectorConfiguration.dateOfLastDownload = DEFAULT_DATE_OF_LAST_DOWNLOAD;
        }
    }

    public static long getMillisecondsBetweenGtfsChecks() {
        return millisecondsBetweenGtfsChecks;
    }

    @Value("${gtfs.millisecondsBetweenGtfsChecks:900000}")
    public void setSecondsBetweenChecks(String secondsBetweenChecks) {
        if (!secondsBetweenChecks.isEmpty()) {
            GtfsCollectorConfiguration.millisecondsBetweenGtfsChecks = Integer.parseInt(secondsBetweenChecks);
        } else {
            GtfsCollectorConfiguration.millisecondsBetweenGtfsChecks = DEFAULT_SECONDS_BETWEEN_CHECKS_IN_MILLISECONDS;
        }
    }

    public static String getSchedulesLocation() {
        return schedulesLocation;
    }

    @Value("${gtfs.schedules.location:/tmp/gtfs}")
    public void setSchedulesLocation(String schedulesLocation) {
        GtfsCollectorConfiguration.schedulesLocation = schedulesLocation;
    }

    public static String getRescheduleUrl() {
        return rescheduleUrl;
    }

    @Value("${gtfs.reschedule.url:}")
    public void setRescheduleUrl(String rescheduleUrl) {
        if (!rescheduleUrl.isEmpty()) {
            GtfsCollectorConfiguration.rescheduleUrl = rescheduleUrl;
        } else {
            GtfsCollectorConfiguration.rescheduleUrl = DEFAULT_RESCHEDULE_URL;
        }
    }

    public static List<String> getAgencies() {
        return agencies;
    }

    @Value("${gtfs.agencies:}")
    public void setAgencies(String agencies) {
        if (!agencies.isEmpty()) {
            GtfsCollectorConfiguration.agencies = parseList(agencies);
        } else {
            GtfsCollectorConfiguration.agencies = DEFAULT_LIST_OF_AGENCIES;
        }
    }


    @Value("${gtfs.backup.files.prefixes:}")
    public void setBackupFilesPrefixes(String prefixes) {
        if (!prefixes.isEmpty()) {
            GtfsCollectorConfiguration.backupFilesPrefixes = parseList(prefixes);
        } else {
            GtfsCollectorConfiguration.backupFilesPrefixes = DEFAULT_LIST_OF_BACKUP_FILE_PREFIXES;
        }
    }

    public static int getGtfsBackupFilesStoreTimeInDays() {
        return gtfsBackupFilesStoreTimeInDays;
    }

    @Value("${gtfs.backup.files.store.time.in.days:}")
    public void setGtfsBackupFilesStoreTimeInDays(String gtfsBackupFilesStoreDays) {
        if (!gtfsBackupFilesStoreDays.isEmpty()) {
            GtfsCollectorConfiguration.gtfsBackupFilesStoreTimeInDays = Integer.parseInt(gtfsBackupFilesStoreDays);
        } else {
            GtfsCollectorConfiguration.gtfsBackupFilesStoreTimeInDays = DEFAULT_BACKUP_FILES_STORE_TIME_IN_DAYS;
        }

    }

    public static List<String> getBackupFilesPrefixes() {
        return backupFilesPrefixes;
    }

    private List<String> parseList(String s) {
        s = s.substring(1+s.indexOf("["), s.lastIndexOf("]"));
        String[] items = s.split(",");
        return new ArrayList<>(Arrays.asList(items));
    }
}
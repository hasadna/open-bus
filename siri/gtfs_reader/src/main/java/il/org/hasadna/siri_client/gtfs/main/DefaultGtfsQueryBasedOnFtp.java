package il.org.hasadna.siri_client.gtfs.main;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import il.org.hasadna.siri_client.gtfs.analysis.SchedulingDataCreator;
import il.org.hasadna.siri_client.gtfs.crud.Route;
import net.jodah.failsafe.Failsafe;
import net.jodah.failsafe.RetryPolicy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.time.format.ResolverStyle;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import il.org.hasadna.siri_client.gtfs.analysis.GtfsDataManipulations;
import il.org.hasadna.siri_client.gtfs.analysis.GtfsRecord;
import il.org.hasadna.siri_client.gtfs.crud.GtfsCrud;
import il.org.hasadna.siri_client.gtfs.crud.GtfsFtp;
import il.org.hasadna.siri_client.gtfs.crud.GtfsZipFile;

import static java.time.temporal.ChronoField.*;

public class DefaultGtfsQueryBasedOnFtp {

    private static Logger logger = LoggerFactory.getLogger(DefaultGtfsQueryBasedOnFtp.class);

    ConfigProperties configProperties = new ConfigProperties();

    LocalDate dateOfLastReschedule = LocalDate.of(2000, 1, 1);

    private LocalDate date;

    private GtfsCrud gtfsCrud;

    public DefaultGtfsQueryBasedOnFtp() {
        configProperties.initFromSystemProperties();
    }

    public DefaultGtfsQueryBasedOnFtp(LocalDate date) throws IOException {
        this.date = date;
        Path gtfsZip = new GtfsFtp().downloadGtfsZipFile();
        if (gtfsZip != null) {
            GtfsZipFile gtfsZipFile = new GtfsZipFile(gtfsZip);
            gtfsCrud = new GtfsCrud(gtfsZipFile);
        }
    }

    public Collection<GtfsRecord> exec() throws IOException {
        return new GtfsDataManipulations(gtfsCrud).combine(date);
    }

    public static void main(String[] args) {
        new DefaultGtfsQueryBasedOnFtp().scheduleGtfs();
    }

    public boolean run() {
        return run(true);
    }

    public boolean run(boolean download) {
        boolean dlOk = true;
        try {
            logger.info("reading gtfs file");
            if (configProperties.disableDownload) {
                logger.trace("download disabled, return without any change");
                return dlOk;
            }
            Path olderGtfs = GtfsFtp.findOlderGtfsFile(LocalDate.now());    // might be null if no files were found
            Path pathToGtfsFile = olderGtfs;    // default value, if we can't download a new GTFS
            if (download) {
                if (!configProperties.skipGtfs) {
                    pathToGtfsFile = new GtfsFtp().downloadGtfsZipFile();
                }
                try {
                    Path makatFile = new GtfsFtp().downloadMakatZipFile();
                    logger.info("makat file read done - {}", makatFile.toFile().getAbsolutePath());
                } catch (Exception ex) {
                    dlOk = false;
                    logger.error("absorbing exception during download of makat file", ex);
                }
            }

            if (pathToGtfsFile == null) {
                dlOk = false;
                throw new IllegalArgumentException("no GTFS files were found");
            }
            GtfsZipFile gtfsZipFile = new GtfsZipFile(pathToGtfsFile);
            gtfsCrud = new GtfsCrud(gtfsZipFile);

            GtfsDataManipulations gtfs = new GtfsDataManipulations(gtfsCrud);
            date = LocalDate.now();
            Collection<GtfsRecord> records = gtfs.combine(date);
            logger.info("size: {}", records.size());

            SchedulingDataCreator schedulingDataCreator = new SchedulingDataCreator();
            schedulingDataCreator.createScheduleForSiri(records, gtfs, configProperties.schedulesLocation, configProperties.agencies, date);

            int result = informSiriJavaClientToReschedule();
            if (result == 200) {
                logger.trace("updating dateOfLastReschedule to {}", LocalDate.now());
                dateOfLastReschedule = LocalDate.now();
            }
        }
        catch (IOException e) {
            logger.error("unhandled exception in main", e);
        }
        catch (Exception e) {
            logger.error("unhandled exception in main", e);
        }
        return dlOk;
    }

    private int informSiriJavaClientToReschedule() {
        RetryPolicy retryPolicy = new RetryPolicy()
                .retryOn(Exception.class)
                .retryIf(result -> (Integer)result != 200)
                .withBackoff(1, 20 * 60, TimeUnit.SECONDS)
                .withMaxRetries(10);

        Integer result = Failsafe.with(retryPolicy).get(() -> sendHttpRequest());
        return result;
    }

    private int sendHttpRequest() {
        //call http GET localhost:8080/data/schedules/read/all
        try {
            logger.info("calling API to reschedule all...");
            URL url = new URL("http://localhost:8080/data/schedules/read/all");
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("GET");
            int status = con.getResponseCode();
            logger.info(" ... Done. status = {}", status);
            return status;
        } catch (Exception e) {
            logger.error("calling API schedules/read/all failed", e);
            logger.trace("(this will cause another download of the GTFS in 15 minutes)");
            //return 0 ;
            throw new RuntimeException(e);  // the exception will cause the Retry mechanism to work
        }
    }


    public void scheduleGtfs() {
        logger.info("Scheduler Started!");

        while (true) {
            LocalTime now = LocalTime.now();
            LocalDate dnow = LocalDate.now();
            logger.trace("check if it is time to replace gtfs...");
            if (now.isAfter(configProperties.whenToDownload)) {
                // do download, but only if it wasn't already done
                if (dnow.isAfter(configProperties.dateOfLastDownload)) {
                    logger.trace("start retrieving GTFS of {}", dnow.toString());

                    // do download
                    boolean downloadOk = run();

                    // signify that dl was done
                    if (downloadOk) {
                        configProperties.dateOfLastDownload = dnow;
                        logger.info("updated dateOfLastDownload to {}", configProperties.dateOfLastDownload.toString());
                    }
                }
                else if (dnow.isAfter(dateOfLastReschedule)) {
                    // do not download, but we must reschedule
                    // because it is another day...
                    run(false);
                }
                else {
                    logger.trace(" ... already downloaded gtfs today");
                }
            }
            else {
                logger.trace(" ... not yet.");
            }

            try {
                logger.trace(" sleeping {} seconds... ", configProperties.secondsBetweenChecks);
                Thread.sleep(configProperties.secondsBetweenChecks * 1000);
            } catch (InterruptedException e) {   }

        }
    }


    public class ConfigProperties {
        Boolean downloadTodaysFile = true;
        Boolean disableDownload = false;
        LocalTime whenToDownload = LocalTime.of(3, 30);
        LocalDate dateOfLastDownload = LocalDate.of(2000, 1, 1);
        Integer secondsBetweenChecks = 15 * 60; // 15 minutes
        String schedulesLocation = "/home/evyatar/logs/";
        String rescheduleUrl = "http://localhost:8080/data/schedules/read/all";
        List<String> agencies = Arrays.asList("5"); // , "16" , "3"
        Boolean skipGtfs = false;

        public void initFromSystemProperties() {
            downloadTodaysFile = Boolean.parseBoolean( fromSystemProp("gtfs.downloadToday", downloadTodaysFile.toString()) );
            disableDownload = Boolean.parseBoolean( fromSystemProp("gtfs.disableDownload", disableDownload.toString()) );
            whenToDownload = LocalTime.parse( fromSystemProp("gtfs.whenToDownload", whenToDownload.toString()) , DateTimeFormatter.ofPattern("HH:mm") );
            dateOfLastDownload = LocalDate.parse( fromSystemProp("gtfs.dateOfLastDownload", dateOfLastDownload.toString()) , DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            secondsBetweenChecks = Integer.parseInt( fromSystemProp("gtfs.secondsBetweenChecks", secondsBetweenChecks.toString() ) );
            schedulesLocation = fromSystemProp("gtfs.schedules.location", schedulesLocation);
            rescheduleUrl = fromSystemProp("gtfs.reschedule.url", rescheduleUrl);
            agencies = parseList(fromSystemProp("gtfs.agencies", agencies.toString()));
            skipGtfs = Boolean.parseBoolean( fromSystemProp("gtfs.skip", skipGtfs.toString()) );
        }

        private List<String> parseList(String s) {
            s = s.substring(1+s.indexOf("["), s.lastIndexOf("]"));
            String[] items = s.split(",");
            return new ArrayList<>(Arrays.asList(items));
        }

        private String fromSystemProp(String propName, String defaultValue) {
            String val = System.getProperty(propName);
            if (val == null) {
                return defaultValue;
            }
            else {
                return val ;
            }
        }
    }
}

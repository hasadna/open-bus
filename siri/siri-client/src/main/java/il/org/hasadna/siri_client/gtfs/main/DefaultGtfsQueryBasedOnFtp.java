package il.org.hasadna.siri_client.gtfs.main;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import il.org.hasadna.siri_client.gtfs.analysis.SchedulingDataCreator;
import il.org.hasadna.siri_client.gtfs.crud.Route;
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


    private LocalDate date;

    private GtfsCrud gtfsCrud;

    public DefaultGtfsQueryBasedOnFtp() {
        configProperties.initFromSystemProperties();
    }

    public DefaultGtfsQueryBasedOnFtp(LocalDate date) throws IOException {
        this.date = date;
        logger.info("111");
        Path gtfsZip = new GtfsFtp().downloadGtfsZipFile();
        logger.info("222");
        GtfsZipFile gtfsZipFile = new GtfsZipFile(gtfsZip);
        logger.info("333");
        gtfsCrud = new GtfsCrud(gtfsZipFile);
        logger.info("444");
    }

    public Collection<GtfsRecord> exec() throws IOException {
        return new GtfsDataManipulations(gtfsCrud).combine(date);
    }

    public static void main(String[] args) {
        //new DefaultGtfsQueryBasedOnFtp().run();
        new DefaultGtfsQueryBasedOnFtp().scheduleGtfs();
    }

    public void run() {
        try {
            logger.info("reading gtfs file");
            if (configProperties.disableDownload) {
                logger.trace("download disabled, return without any change");
                return;
            }
            GtfsZipFile gtfsZipFile = new GtfsZipFile(new GtfsFtp().downloadGtfsZipFile());
            date = LocalDate.now();
            gtfsCrud = new GtfsCrud(gtfsZipFile);
            GtfsDataManipulations gtfs = new GtfsDataManipulations(gtfsCrud);
            Collection<GtfsRecord> records = gtfs.combine(date);
            logger.info("size: {}", records.size());

            SchedulingDataCreator schedulingDataCreator = new SchedulingDataCreator();
            schedulingDataCreator.createScheduleForSiri(records, gtfs);

            informSiriJavaClientToReschedule();
        }
        catch (IOException e) {
            logger.error("unhandled exception in main", e);
        }
        catch (Exception e) {
            logger.error("unhandled exception in main", e);
        }
    }

    private int informSiriJavaClientToReschedule() {
        //call http GET localhost:8080/data/schedules/read/all
        try {
            logger.info("calling API to reschedule all...");
            URL url = new URL("http://localhost:9003/data/schedules/read/all");
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("GET");
            int status = con.getResponseCode();
            logger.info(" ... Done. status = {}", status);
            return status;
        } catch (Exception e) {
            logger.error("calling API schedules/read/all failed", e);
            return 0 ;
        }
    }


    public void scheduleGtfs() {
        logger.trace("Scheduler Started!");
        while (true) {
            try {
                Thread.sleep(configProperties.secondsBetweenChecks * 1000);
            } catch (InterruptedException e) {   }

            logger.trace("check if it is time to replace gtfs...");
            if (LocalTime.now().isAfter(configProperties.whenToDownload)) {
                // do download, but only if it wasn't already done
                if (LocalDate.now().isAfter(configProperties.dateOfLastDownload)) {
                    logger.trace("start retrieving GTFS of {}", LocalDate.now().toString());

                    // do download
                    run();

                    // signify that dl was done
                    configProperties.dateOfLastDownload = LocalDate.now();
                    logger.trace("updated dateOfLastDownload to {}", configProperties.dateOfLastDownload.toString());
                }
                else {
                    logger.trace(" ... already downloaded gtfs today");
                }
            }
            else {
                logger.trace(" ... not yet.");
            }

        }
    }


    private class ConfigProperties {
        Boolean downloadTodaysFile = true;
        Boolean disableDownload = false;
        LocalTime whenToDownload = LocalTime.of(3, 30);
        LocalDate dateOfLastDownload = LocalDate.of(2000, 1, 1);
        Integer secondsBetweenChecks = 60;

        public void initFromSystemProperties() {
            downloadTodaysFile = Boolean.parseBoolean( fromSystemProp("gtfs.downloadToday", downloadTodaysFile.toString()) );
            disableDownload = Boolean.parseBoolean( fromSystemProp("gtfs.disableDownload", disableDownload.toString()) );
            whenToDownload = LocalTime.parse( fromSystemProp("gtfs.whenToDownload", whenToDownload.toString()) , DateTimeFormatter.ofPattern("HH:mm") );
            dateOfLastDownload = LocalDate.parse( fromSystemProp("gtfs.dateOfLastDownload", dateOfLastDownload.toString()) , DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            secondsBetweenChecks = Integer.parseInt( fromSystemProp("gtfs.secondsBetweenChecks", secondsBetweenChecks.toString() ) );
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

package il.org.hasadna.siri_client.gtfs.main;

import il.org.hasadna.siri_client.gtfs.analysis.GtfsDataManipulations;
import il.org.hasadna.siri_client.gtfs.analysis.GtfsRecord;
import il.org.hasadna.siri_client.gtfs.analysis.SchedulingDataCreator;
import il.org.hasadna.siri_client.gtfs.crud.DownloadFailedException;
import il.org.hasadna.siri_client.gtfs.crud.GtfsCrud;
import il.org.hasadna.siri_client.gtfs.crud.GtfsFtp;
import il.org.hasadna.siri_client.gtfs.crud.GtfsZipFile;
import il.org.hasadna.siri_client.gtfs.service.SiriCollectorClient;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.Collection;
import java.util.Optional;
import javax.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

@Service
@EnableScheduling
public class GtfsCollectorService {
  private SiriCollectorClient siriCollectorClient;
  private GtfsFtp gtfsFtp;
  private LocalDate dateOfLastReschedule;
  private LocalDate dateOfLastDownload;

  @Autowired
  public GtfsCollectorService(SiriCollectorClient siriCollectorClient, GtfsFtp gtfsFtp) {
    this.siriCollectorClient = siriCollectorClient;
    this.gtfsFtp = gtfsFtp;
  }

  @PostConstruct
  public void init() {
    dateOfLastDownload = GtfsCollectorConfiguration.getDateOfLastDownload();
  }

  private static Logger logger = LoggerFactory.getLogger(GtfsCollectorService.class);

  public void run() {
    run(true);
  }

  public void run(boolean download) {
    try {
      logger.info("reading gtfs file");
      if (GtfsCollectorConfiguration.getGtfsDownloadDisabled()) {
        logger.trace("download disabled, return without any change");
        return;
      }

      Path pathToGtfsFile = null;

      if (download) {
        pathToGtfsFile = gtfsFtp.downloadGtfsZipFile();

        try {
          Path makatFile = gtfsFtp.downloadMakatZipFile();
          logger.info("makat file read done - {}", makatFile.toFile().getAbsolutePath());
        } catch (Exception ex) {
          logger.error("absorbing exception during download of makat file", ex);
        }
      }

      if (pathToGtfsFile == null) {
        Optional<Path> optionalOldGtfs = GtfsFtp.findOlderGtfsFile(LocalDate.now());
        if (!optionalOldGtfs.isPresent()) {
          throw new DownloadFailedException("failed to download gtfs file and no old gtfs file found.");
        }

        pathToGtfsFile = optionalOldGtfs.get();
      }

      GtfsZipFile gtfsZipFile = new GtfsZipFile(pathToGtfsFile);
      GtfsCrud gtfsCrud = new GtfsCrud(gtfsZipFile);

      GtfsDataManipulations gtfs = new GtfsDataManipulations(gtfsCrud);
      LocalDate currentDate = LocalDate.now();
      Collection<GtfsRecord> records = gtfs.combine(currentDate);
      logger.info("size: {}", records.size());

      SchedulingDataCreator schedulingDataCreator = new SchedulingDataCreator();
      schedulingDataCreator.createScheduleForSiri(records, gtfs,
          GtfsCollectorConfiguration.getSchedulesLocation(), GtfsCollectorConfiguration.getAgencies(), currentDate);

      int responseStatus = siriCollectorClient.reschedule();
      if (responseStatus == HttpStatus.OK.value()) {
        logger.trace("updating dateOfLastReschedule to {}", LocalDate.now());
        dateOfLastReschedule = LocalDate.now();
      }

    } catch (Exception e) {
      logger.error("unhandled exception in main", e);
    }
  }

  @Scheduled(fixedDelayString = "${gtfs.millisecondsBetweenGtfsChecks:900000}")
  public void scheduleGtfs() {
    logger.trace("Scheduler Started!");

    LocalTime now = LocalTime.now();
    LocalDate dnow = LocalDate.now();
    logger.trace("check if it is time to replace gtfs...");
    if (now.isAfter(GtfsCollectorConfiguration.getWhenToDownload())) {
      // do download, but only if it wasn't already done
      if (dnow.isAfter(dateOfLastDownload)) {
        logger.trace("start retrieving GTFS of {}", dnow.toString());

        // do download
        run();

        // signify that dl was done
        dateOfLastDownload = dnow;

        logger.trace("updated dateOfLastDownload to {}", dateOfLastDownload);
      } else if (dnow.isAfter(dateOfLastReschedule)) {
        // do not download, but we must reschedule
        // because it is another day...
        run(false);
      } else {
        logger.trace(" ... already downloaded gtfs today");
      }
    } else {
      logger.trace(" ... not yet.");
    }

    logger.trace(" sleeping {} milliseconds... ", GtfsCollectorConfiguration.getMillisecondsBetweenGtfsChecks());
  }
}

package il.org.hasadna.siri_client.gtfs.main;

import il.org.hasadna.siri_client.gtfs.crud.GtfsCrud;
import java.time.LocalDate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;

public class GtfsCollectorStartup {
  private static final String SPRING_APPLICATION_CONTEXT_FILENAME = "applicationContext.xml";
  private static final String SERVICE_NAME = "gtfs-collector";

  private static Logger logger = LoggerFactory.getLogger(GtfsCollectorStartup.class);

  private static LocalDate dateOfLastReschedule = LocalDate.of(2000, 1, 1);

  private static LocalDate date;

  private static GtfsCrud gtfsCrud;

  @Autowired
  GtfsCollectorConfiguration gtfsCollectorConfiguration;

  @Autowired
  private static GtfsCollectorService gtfsCollectorService;

  public static void main(String[] args) throws InterruptedException {
    logger.info("starting {}!", SERVICE_NAME);

    ApplicationContext context = new ClassPathXmlApplicationContext(SPRING_APPLICATION_CONTEXT_FILENAME);
    gtfsCollectorService = context.getBean(GtfsCollectorService.class);

    Thread.sleep(Long.MAX_VALUE);
  }
}

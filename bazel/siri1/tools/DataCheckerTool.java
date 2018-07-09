package bazel.tools;

import com.google.common.collect.ImmutableList;
import com.google.startupos.common.CommonModule;
import com.google.common.flogger.FluentLogger;
import com.google.startupos.common.flags.Flags;
import com.google.common.base.Strings;
import com.google.common.flogger.FluentLogger;
import com.google.startupos.common.FileUtils;
import com.google.startupos.common.flags.Flag;
import com.google.startupos.common.flags.FlagDesc;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import dagger.Component;
import javax.inject.Inject;
import javax.inject.Singleton;

import bazel.tools.Proto.RawData;
import bazel.tools.Proto.RawDataList;


/*
* A tool to check validity of SIRI data.
*/
@Singleton
public class DataCheckerTool {

  private static final FluentLogger log = FluentLogger.forEnclosingClass();

  @FlagDesc(name = "input_csv", description = "Path to input Siri CSV file")
  public static final Flag<String> inputCsv = Flag.create("");
  @FlagDesc(name = "output_protobin", description = "Path to output protobin file")
  public static final Flag<String> outputProtobin = Flag.create("");

  public enum Columns {
    TIMESTAMP,
    DESCRIPTION,
    OPERATOR_REF,
    LINE_REF,
    LINE_NAME,
    JOURNEY_REF,
    DEPARTURE_TIME,
    LICENSE_PLATE,
    EXPECTED_ARRIVAL_TIME,
    RECORDED_AT,
    LONGITUDE,
    LATITUDE
  }

  private static DateFormat DATE_FORMATTER_WITH_MS = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.S");
  private static DateFormat DATE_FORMATTER_WITHOUT_MS = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
  private static DateFormat TIME_FORMATTER = new SimpleDateFormat("HH:mm");


  public RawDataList getRawDataList() {
    RawDataList.Builder result = RawDataList.newBuilder();

    try {
      Reader fileReader = new FileReader(fileUtils.expandHomeDirectory(inputCsv.get()));
      List<CSVRecord> records =
          CSVFormat.DEFAULT
              .withDelimiter(',')
              .withHeader(Columns.class)
              .parse(fileReader)
              .getRecords();

      for (CSVRecord record : records) {
        long timestamp = parseDate(record.get(Columns.TIMESTAMP));
        long operatorRef = parseLong(record.get(Columns.OPERATOR_REF));
        long departureTime = parseTime(record.get(Columns.DEPARTURE_TIME));
        long expectedArrivalTime = parseTime(record.get(Columns.EXPECTED_ARRIVAL_TIME));
        long recordedAt = parseTime(record.get(Columns.RECORDED_AT));
        double longitude = parseDouble(record.get(Columns.LONGITUDE));
        double latitude = parseDouble(record.get(Columns.LATITUDE));

        RawData rawData =
            RawData.newBuilder()
                .setTimestamp(timestamp)
                .setDescription(record.get(Columns.DESCRIPTION))
                .setOperatorRef(operatorRef)
                .setLineRef(record.get(Columns.LINE_REF))
                .setLineName(record.get(Columns.LINE_NAME))
                .setJourneyRef(record.get(Columns.JOURNEY_REF))
                .setDepartureTime(departureTime)
                .setLicensePlate(record.get(Columns.LICENSE_PLATE))
                .setExpectedArrivalTime(expectedArrivalTime)
                .setLongitude(longitude)
                .setLatitude(latitude)
                .build();
        result.addRawData(rawData);
      }
    } catch (IOException | ParseException e) {
      throw new RuntimeException(e);
    }

    return result.build();
  }

  private static Double parseDouble(String value) {
    return Strings.isNullOrEmpty(value) ? null : Double.valueOf(value);
  }

  private static Long parseLong(String value) {
    return Strings.isNullOrEmpty(value) ? null : Long.valueOf(value);
  }

  private static long parseDate(String dateString) throws ParseException {
    try {
      return DATE_FORMATTER_WITH_MS.parse(dateString).getTime();
    } catch (ParseException e) {
      return DATE_FORMATTER_WITHOUT_MS.parse(dateString).getTime();
    }
  }

  private static long parseTime(String timeString) throws ParseException {
    return TIME_FORMATTER.parse(timeString).getTime();
  }

  FileUtils fileUtils;

  @Inject
  DataCheckerTool(FileUtils fileUtils) {
    this.fileUtils = fileUtils;
  }

  public void run() {
    RawDataList dataList = getRawDataList();
    fileUtils.writeProtoBinaryUnchecked(dataList, outputProtobin.get());
  }

  @Singleton
  @Component(modules = { CommonModule.class })
  interface MainComponent {
    DataCheckerTool getDataCheckerTool();
  }

  public static void main(String[] args) {
    Flags.parse(args, DataCheckerTool.class.getPackage());
    DaggerDataCheckerTool_MainComponent.create().getDataCheckerTool().run();
  }
}
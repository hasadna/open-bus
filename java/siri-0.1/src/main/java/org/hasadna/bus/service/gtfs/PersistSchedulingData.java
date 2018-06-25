package org.hasadna.bus.service.gtfs;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.hasadna.bus.service.Command;
import org.hasadna.bus.service.SchedulingData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Paths;
import java.util.List;

public class PersistSchedulingData {

    protected final static Logger logger = LoggerFactory.getLogger("console");


    public static void main(String args[]) {
        ObjectMapper mapper = new ObjectMapper();
        String content = "{ \"dummy\": \"1\",\n" +
                "  \"d\" : [ {\"stopCode\" : \"20594\"} ] }";
        try {
            SchedulingData data = mapper.readValue(new StringReader(content), SchedulingData.class);
            logger.info("read data: {}", data);
            List<Command> list = data.d;
            logger.info("list has {} elements", list.size());
        } catch (IOException e) {
            logger.error("error during reading data file", e);
        }
    }
}

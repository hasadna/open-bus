package org.hasadna.bus.controller;

import org.hasadna.bus.service.SiriConsumeService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/gtfs")
public class GtfsController {


    protected final Logger logger = LoggerFactory.getLogger(this.getClass());

    @Autowired
    SiriConsumeService siriConsumeService;

    // returns details about lineref, including the line published name, and list of stopCodes for all its stops
    @RequestMapping(value="/line/ref/{lineRef}", method={RequestMethod.GET}, produces = "application/xml")
    public String retrieveLineRefDetails(@PathVariable String lineRef) {
        logger.info("line/ref/{} ", lineRef);
        String result = "Not Implemented yet";
        return result;
    }

    // return details about the specified stop (identified by its stopCode)
    @RequestMapping(value="/stop/details/{stopCode}", method={RequestMethod.GET}, produces = "application/xml")
    public String retrieveStopDetails(@PathVariable String stopCode) {
        logger.info("stop/details/{} ", stopCode);
        String result = "Not Implemented yet";
        return result;
    }
}

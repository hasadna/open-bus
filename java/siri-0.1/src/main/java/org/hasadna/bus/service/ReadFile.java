package org.hasadna.bus.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Component
public class ReadFile {

    protected final Logger logger = LoggerFactory.getLogger(this.getClass());

    @Cacheable("files")
    public String readFromFile(String name) {
        String fileName = name + ".xml";
        try {
            Path path = Paths.get(getClass().getClassLoader().getResource("samples/" + fileName).toURI());
            String content = new String(Files.readAllBytes(path), Charset.forName("UTF8"));
            return content;
        } catch (IOException e) {
            logger.error("can't read file", e);
        } catch (URISyntaxException e) {
            logger.error("can't read file", e);
        }
        return null;
    }

}

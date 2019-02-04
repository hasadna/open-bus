package org.hasadna.openbus.siri_retriever;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class SiriRetrieverApplication {

    public static void main(String[] args) {
        SpringApplication.run(SiriRetrieverApplication.class, args);
    }
}

package org.hasadna.bus.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Recover;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Component;
import org.springframework.util.StopWatch;
import org.springframework.web.client.*;

@Component
public class HttpPostRestTemplateImpl implements HttpPost {

    protected final Logger logger = LoggerFactory.getLogger(this.getClass());

    @Autowired
    RestTemplateBuilder restTemplateBuilder;

    /**
     * This implementation of post http request uses the Spring Retry functionality.
     * This configuration or retryable
     * value = { HttpServerErrorException.class }, maxAttempts = 5, backoff = @Backoff(delay = 1000, multiplier = 2)
     * will execute 5 attempts (if needed), with initial delay of 1 second. The delay will be
     * multiplied by 2 for each sunsequent attempt (Exponential Backoff).
     * An attempt will be considered as failed if HttpServerErrorException is thrown by the method.
     * We have seen Siri returning HttpServerErrorException: 503 Service Unavailable
     * on several occasions.
     * If after 5 attempts there is still no proper answer from Siri, the method will return null.
     *
     * @param url
     * @param entity
     * @return
     */
    @Override
    @Retryable(value = {HttpClientErrorException.class, HttpServerErrorException.class},
            maxAttempts = 5, backoff = @Backoff(delay = 1000, multiplier = 2))
    public ResponseEntity<String> postHttpRequest(String url, HttpEntity<String> entity) {
        StopWatch sw = new StopWatch(Thread.currentThread().getName());
        sw.start();

        // we must use the builder, in order to get all its predefined meters.
        // see https://docs.spring.io/spring-boot/docs/current-SNAPSHOT/reference/html/production-ready-metrics.html#production-ready-metrics-http-clients
        // The pre-defined name of the meter is http.client.requests
        // so in DataDog we will see Metrics with the following names:
        // http.client.requests.count - how many requests in the last minute (throughput)
        // http.client.requests.avg - average response time (latency), in milliseconds, for the last minute
        // http.client.requests.max - maximal response time in the last minute, in milliseconds
        // http.client.requests.sum - sum of all response times in the last minute (in milliseconds)
        // it seems that currently we can't display histograms in DataDog.
        RestTemplate restTemplate = restTemplateBuilder.build();
        ResponseEntity<String> r = null;
        try {
            logger.debug("url={}", url);
            logger.debug("requestXml={}", entity.getBody().replaceAll("\n", ""));
            r = restTemplate.postForEntity(url, entity, String.class);
        } catch (ResourceAccessException ex) {
            logger.error("absorbing unhandled", ex);
            return null;
        } catch (HttpServerErrorException ex) {
            // probably 503 Service Unavailable (but for the new 2.7 address we see 500 Internal Server Error)
            // backpressure - reduce frequency of requests until MOT Siri service is up again
            logger.error("handling exception, will retry the same request", ex);
            try {
                logger.error("status code {}", ex.getRawStatusCode());
                logger.error("most specific cause: {}", ex.getMostSpecificCause()); ;
            } catch (Exception e) { ; }
            throw ex;
        } catch (HttpClientErrorException ex) {
            // probably 408 Request Time-out
            // backpressure - reduce frequency of requests until MOT Siri service is up again
            logger.error("handling exception, will retry the same request", ex);
            try {
                logger.error("status code {}", ex.getRawStatusCode());
                logger.error("most specific cause: {}", ex.getMostSpecificCause()); ;
            } catch (Exception e) { ; }
            throw ex;
        }
        catch (RestClientException ex) {
            logger.error("absorbing unhandled", ex);
            return null;
        }
        catch (Exception ex) {
            logger.error("absorbing unexpected", ex);
            return null;
        }
        sw.stop();
        logger.debug("network to MOT server: {} ms", sw.getTotalTimeMillis());
        return r;
    }

    /** this method takes care that after the last attempt,
     * if still no proper answer, the method will return null
     * @param ex
     * @return  null (called only after X attempts as configured above)
     */
    @Recover
    public Double recover(HttpServerErrorException ex) {
        return null;
    }

}
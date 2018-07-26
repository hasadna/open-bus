package org.hasadna.bus.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Recover;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Component;
import org.springframework.util.StopWatch;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

@Component
public class HttpPostRestTemplateImpl implements HttpPost {

    protected final Logger logger = LoggerFactory.getLogger(this.getClass());

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
    @Retryable(value = {HttpServerErrorException.class},
            maxAttempts = 5, backoff = @Backoff(delay = 1000, multiplier = 2))
    public ResponseEntity<String> postHttpRequest(String url, HttpEntity<String> entity) {
        StopWatch sw = new StopWatch(Thread.currentThread().getName());
        sw.start();

        RestTemplate restTemplate = new RestTemplate();

        ResponseEntity<String> r = null;
        try {
            r = restTemplate.postForEntity(url, entity, String.class);
        } catch (ResourceAccessException ex) {
            logger.error("absorbing unhandled", ex);
            return null;
        } catch (HttpServerErrorException ex) {
            // probably 503 Service Unavailable
            // backpressure - reduce frequency of requests until MOT Siri service is up again
            logger.error("handling exception, will retry the same request", ex);
            throw ex;
        } catch (RestClientException ex) {
            logger.error("absorbing unhandled", ex);
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
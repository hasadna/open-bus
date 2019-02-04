package org.hasadna.bus.service;

import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;

public interface HttpPost {
    ResponseEntity<String> postHttpRequest(String url, HttpEntity<String> entity);
}

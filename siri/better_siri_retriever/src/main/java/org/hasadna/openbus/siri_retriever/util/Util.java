package org.hasadna.openbus.siri_retriever.util;

public class Util {

    public static String removeSoapEnvelope(String content) {
        // remove soap envelope (ugly)
        content = content.trim();   // remove whitespaces, including newlines in the end of line
        final String prefix = "<?xml version='1.0' encoding='UTF-8'?><S:Envelope xmlns:S=\"http://schemas.xmlsoap.org/soap/envelope/\"><S:Body>";
        final String suffix = "</S:Body></S:Envelope>";
        if (content.startsWith(prefix)) {
            content = content.substring(prefix.length());
        }
        if (content.endsWith(suffix)) {
            content = content.substring(0,content.length()-suffix.length());
        }
        return content;
    }
}

package org.hasadna.bus.util;

public class SoapUtils {

    public static String removeSoapEnvelope(String content) {
        // remove soap envelope (ugly)
        content = content.trim();   // remove whitespaces, including newlines in the end of line
        final String prefix1 = "<?xml version='1.0' encoding='UTF-8'?>";
        final String prefix2 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
        if (content.startsWith(prefix1)) {
            content = content.substring(prefix1.length());
        }
        else if (content.startsWith(prefix2)) {
            content = content.substring(prefix2.length());
        }
        else {
            // TODO log
        }
        final String prefix = "<S:Envelope xmlns:S=\"http://schemas.xmlsoap.org/soap/envelope/\"><S:Body>";
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

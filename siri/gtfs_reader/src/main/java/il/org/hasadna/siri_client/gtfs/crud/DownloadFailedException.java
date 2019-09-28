package il.org.hasadna.siri_client.gtfs.crud;

import java.io.IOException;

public class DownloadFailedException extends IOException {

    public DownloadFailedException(String message) {
        super(message);
    }

    public DownloadFailedException(Throwable cause) {
        super(cause);
    }
}

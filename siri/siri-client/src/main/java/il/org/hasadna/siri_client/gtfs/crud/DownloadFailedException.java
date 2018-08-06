package il.org.hasadna.siri_client.gtfs.crud;

import java.io.IOException;

public class DownloadFailedException extends IOException {
    public DownloadFailedException() {
        super();
    }
    public DownloadFailedException(String message) {
        super(message);
    }
    public DownloadFailedException(String message, Throwable cause) {
        super(message, cause);
    }


}

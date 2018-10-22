package il.org.hasadna.siri_client.gtfs.crud;

import java.io.IOException;
import java.util.Collection;
import java.util.Collections;
import java.util.stream.Stream;

public interface Crud<T> {

	/**
	 * Read a file line by line and parse each line to T instance
	 * 
	 * @param <T>
	 *            The type of the parsed object
	 * @return Stream of T
	 * @throws IOException
	 *             if an I/O error occurs while reading the file
	 */
	Stream<T> ReadAll() throws IOException;

	
	static class EmptyCrud<T> implements Crud<T>{

		@Override
		public Stream<T> ReadAll() throws IOException {
			Collection<T> coll = Collections.emptyList();
			return coll.stream();
		}
		
	}
}
package il.org.hasadna.siri_client.gtfs.crud;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.stream.Stream;

/**
 * An abstract class that hold a file and read it by parsing each line of it
 * with the abstract method "parseLine"
 * 
 * @author Aviv Sela
 * @param <T>
 *            The type of the parsed object
 */
public abstract class AbstractFileCrud<T> implements Crud<T> {

	protected Path file;

	@Override
	public Stream<T> ReadAll() throws IOException {

		BufferedReader in = new BufferedReader(
				new InputStreamReader(Files.newInputStream(file, StandardOpenOption.READ),"UTF-8"));
		in.readLine();// skip header
		return in.lines()
				.map(i -> parseLine(i));
	}

	abstract T parseLine(String string);

	public AbstractFileCrud(Path file) throws IOException {
		if (!Files.isReadable(file)) {
			throw new IOException("File is not readable");
		}
		this.file = file;
	}

}
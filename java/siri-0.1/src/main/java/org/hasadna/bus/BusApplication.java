package org.hasadna.bus;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

@SpringBootApplication
@EnableScheduling
@EnableCaching
@EnableAsync
public class BusApplication {

	@Value("${pool.process.response.core.pool.size:20}")
	private int poolProcessResponseCorePoolSize ;

	@Value("${pool.process.response.max.pool.size:25}")
	private int poolProcessResponseMaxPoolSize ;

	@Value("${pool.http.retrieve.core.pool.size:5}")
	private int poolHttpRetrieveCorePoolSize ;

	@Value("${pool.http.retrieve.max.pool.size:10}")
	private int poolHttpRetrieveMaxPoolSize ;


	/**
	 * This thread-pool is used for threads that do the processing!
	 * (not the retrieval)
	 * @return
	 */
	@Bean(name = "process-response")
	public Executor threadPoolTaskExecutor() {
		ThreadPoolTaskExecutor x = new ThreadPoolTaskExecutor();
		x.setCorePoolSize(poolProcessResponseCorePoolSize);
		x.setMaxPoolSize(poolProcessResponseMaxPoolSize);
		return x;
	}

	@Bean(name = "http-retrieve")	// scheduler Threads
	public Executor mythreadPoolTaskExecutor() {
		ThreadPoolTaskExecutor x = new ThreadPoolTaskExecutor();
		x.setCorePoolSize(poolHttpRetrieveCorePoolSize);
		x.setMaxPoolSize(poolHttpRetrieveMaxPoolSize);
		return x;
	}

	public static void main(String[] args) {
		SpringApplication.run(BusApplication.class, args);
	}
}

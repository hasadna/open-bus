CREATE TABLE responses(
	id					SERIAL		 PRIMARY KEY,
	response_xml		TEXT     NOT NULL
);

CREATE TABLE arrivals(
	id		SERIAL	PRIMARY KEY,	
	line_ref 		INT     NOT NULL,
	direction_ref           INT    	NOT NULL,
	published_line_name	VARCHAR(10)     NOT NULL,
	operator_ref		INT	NOT NULL,
	destination_ref		INT	NOT NULL,
	monitoring_ref		INT	NOT NULL,
	expected_arrival_time	TIMESTAMP WITH TIME ZONE 	NOT NULL,
	stop_point_ref		INT	NOT NULL,
	response_id			INT REFERENCES responses(id) NOT NULL
);
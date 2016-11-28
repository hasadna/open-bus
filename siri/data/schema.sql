CREATE TABLE IF NOT EXISTS siri_raw_responses (
  id           SERIAL PRIMARY KEY,
  response_xml TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS siri_arrivals (
  id                          SERIAL PRIMARY KEY,
  recorded_at_time            TIMESTAMP WITH TIME ZONE               NOT NULL,
  item_identifier             INT,
  monitoring_ref              INT                                    NOT NULL,
  line_ref                    INT                                    NOT NULL,
  direction_ref               INT                                    NOT NULL,
  operator_ref                INT,
  published_line_name         VARCHAR(10)                            NOT NULL,
  destination_ref             INT                                    NOT NULL,
  dated_vehicle_journey_ref   VARCHAR(10),
  vehicle_ref                 VARCHAR(7),
  confidence_level            VARCHAR(10),
  origin_aimed_departure_time TIMESTAMP WITH TIME ZONE,
  stop_point_ref              INT                                    NOT NULL,
  vehicle_at_stop             BOOLEAN,
  request_stop                BOOLEAN,
  destination_display         TEXT,
  aimed_arrival_time          TIMESTAMP WITH TIME ZONE,
  actual_arrival_time         TIMESTAMP WITH TIME ZONE,
  expected_arrival_time       TIMESTAMP WITH TIME ZONE               NOT NULL,
  arrival_status              VARCHAR(10),
  arrival_platform_name       TEXT,
  arrival_boarding_activity   VARCHAR(11),
  actual_departure_time       TIMESTAMP WITH TIME ZONE,
  aimed_departure_time        TIMESTAMP WITH TIME ZONE,
  stop_visit_note             TEXT,
  response_id                 INT REFERENCES siri_raw_responses (id) NOT NULL
);



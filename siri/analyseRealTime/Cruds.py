import datetime
import psycopg2
import RealTimeArrivals
from RealTimeArrivals import Stop, Record

class InvalidDbState(ValueError):
    """Exception raised when the state of DB is invalid"""
    def __repr__(self):
        return 'The state of db is invalid'

class Connection:
    def __init__(self,**kwargs):
        self._connection_configuration = kwargs
        self.conn = None

    def __enter__(self):
        self.conn = self._init_connection_to_server()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    # this method should return valid db connection.
    def _init_connection_to_server(self):
        return psycopg2.connect(**self._connection_configuration)

class Crud:
    def __init__(self, connection=None):
        if connection:
            self.conn = connection.conn

    def read_records_from_siri(self, trip_id, trip_date):
        return None

    def read_stops(self, trip_id=None):
        return None

    def write_arrivals(self, real_times):
        pass

    def get_relevant_trips_from_gtfs(self, date:datetime.date):
        pass


class CrudPostgresql(Crud):
    def __init__(self, connection):
        super().__init__(connection)

    def read_stops(self, trip_id=None):
        with self.conn.cursor() as curs:
            curs.execute("""SELECT t.trip_id,
                                r.route_short_name,
                                r.route_id,
                                r.Route_long_name,
                                st.arrival_time,
                                st.stop_id,
                                st.Stop_sequence,
                                st.Shape_dist_traveled
                            FROM gtfs_trips t
                                LEFT JOIN gtfs_routes AS r ON t.Route_id = r.route_id
                                JOIN gtfs_stop_times AS st ON st.trip_id = t.trip_id
                            WHERE t.trip_id LIKE '{}'
                            """.format(trip_id))
            data = curs.fetchall()
            if not data:
                raise InvalidDbState("cant find records in gtfs with trip id: {}".format(trip_id))
            return [Stop(*i) for i in data]

    def read_records_from_siri(self, trip_id, trip_date):
        with self.conn.cursor() as curs:
            curs.execute("""SELECT siri_arrivals.trip_id_from_gtfs,
                                siri_arrivals.recorded_at_time,
                                siri_arrivals.vehicle_ref,
                                siri_arrivals.route_offset
                            FROM siri_arrivals
                            WHERE siri_arrivals.trip_id_from_gtfs = '{}'
                                AND '{}' = date_trunc('day',siri_arrivals.recorded_at_time)
                                AND Route_offset IS NOT NULL""".format(trip_id, trip_date))
            data = curs.fetchall()
            if not data:
                raise InvalidDbState("can't get records siri with id: {} and date: {}".format(trip_id,trip_date ))
            data = [ Record(*i) for i in data]
            return data

    def write_arrivals(self, real_times):
        sql = """INSERT INTO public.siri_real_time_arrivals(
                    route_id, trip_id, arrival_time, stop_id, meters_between_records, 
                    seconds_between_records)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT ON CONSTRAINT "PK" DO NOTHING;"""
        with self.conn.cursor() as curs:
            data = [(i.stop.route_id,
                     i.stop.trip_id,
                     i.real_time,
                     i.stop.stop_id,
                     i.records[1].route_offset_in_meters - i.records[0].route_offset_in_meters,
                     (i.records[1].recorded_at_time - i.records[0].recorded_at_time).total_seconds())
                    for i in real_times]

            curs.executemany(sql, data)
            self.conn.commit()

    def get_relevant_trips_from_gtfs(self, date:datetime.date):
        sql = """SELECT trip_id_from_gtfs, date_trunc('day', max(recorded_at_time)) 
        FROM siri_arrivals 
        WHERE recorded_at_time between '{}' and '{}' 
        GROUP BY trip_id_from_gtfs;"""
        with self.conn.cursor() as curs:
            curs.execute(sql.format(date, (date + datetime.timedelta(days=1))))
            return [RealTimeArrivals.Trip(row[0],row[1],self) for row in curs if row[0]]

    def get_sample_of_data(self):
        sql = """select m.trip_id, date_trunc('day',t.recorded_at_time)
                    from (select DISTINCT trip_id
                            from gtfs_trips b
	                        join siri_arrivals a
		                    ON b.trip_id = a.trip_id_from_gtfs
	                        LIMIT 10) as m

                    join siri_arrivals t 
                        on m.trip_id = t.trip_id_from_gtfs
                    group by m.trip_id, date_trunc('day',t.recorded_at_time)
                    limit 15;"""
        with self.conn.cursor() as curs:
            curs.execute(sql)
            return [i for i in curs]
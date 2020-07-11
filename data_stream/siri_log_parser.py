import csv
import sqlite3
from datetime import datetime, time
import gzip
from abc import ABC, abstractmethod
from collections import defaultdict
import json
from typing import Any, Dict

from data_stream.base_classes import SiriRide, SiriRecord, GeoPoint


class RidesCacheMechanism(ABC):  # pragma: no cover
    @abstractmethod
    def add_ride(self, record: SiriRide):
        pass

    @abstractmethod
    def get_rides(self):
        pass

    def commit(self):
        pass


class SqliteRidesCacheMechanism(RidesCacheMechanism):
    def __init__(self, conn: sqlite3.Connection):
        self._create_base_schema(conn)
        self.conn = conn
        self.cache: Dict[Any, int] = dict()

    def _create_record_in_db(self, ride_key: int, item: SiriRecord) -> None:
        self.conn.execute(f"insert into records (key, responseTimestamp, record) "
                          f"values({ride_key}, '{item.response_timestamp}','{json.dumps(item.to_json())}')")

    def _create_ride_in_db(self, ride: SiriRide) -> int:
        params = (ride.line_name, ride.license_plate, ride.operator_ref, ride.line_ref, str(ride.departure_time),
                  ride.journey_ref)

        ride_key = self.cache.get(params)
        if ride_key is not None:
            return ride_key

        cur = self.conn.cursor()
        cur.execute(f"insert into rides (line_name, license_plate, operator_ref, line_ref, departure_time, "
                    f"journey_ref) values(?,?,?,?,?,?)", params)

        self.cache[params] = cur.lastrowid
        return cur.lastrowid

    def add_ride(self, ride: SiriRide):
        ride_key = self._create_ride_in_db(ride)

        for siri_record in ride.siri_records:
            self._create_record_in_db(ride_key, siri_record)

    def get_rides(self):

        rides_rows = self.conn.cursor().execute(
            '''SELECT ride_id,line_name,license_plate,operator_ref,line_ref,departure_time,journey_ref,
                        "[" || GROUP_CONCAT(records.record) || "]" as records
                FROM rides 
                JOIN records 
                    ON rides.ride_id = records.key
                GROUP BY ride_id''')

        for ride_row in rides_rows:
            siri_records = set((SiriRecord.from_json(i) for i in json.loads(ride_row[7])))
            yield SiriRide(line_name=ride_row[1], license_plate=ride_row[2], operator_ref=ride_row[3],
                           line_ref=ride_row[4], departure_time=time.fromisoformat(ride_row[5]),
                           journey_ref=ride_row[6], siri_records=siri_records)

    def commit(self):
        self.conn.commit()

    @staticmethod
    def _create_base_schema(conn: sqlite3.Connection):
        # Create table
        conn.execute('''CREATE TABLE IF NOT EXISTS rides (ride_id INTEGER PRIMARY KEY AUTOINCREMENT, line_name text, 
                            license_plate text, operator_ref text, line_ref text, 
                            departure_time text, journey_ref text)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS records (key number,responseTimestamp text, record text)''')

    def close(self):
        self.conn.close()


class InMemoryRidesCacheMechanism(RidesCacheMechanism):
    def __init__(self):
        self._records = defaultdict(set)

    def add_ride(self, record: SiriRide):
        self._records[(record.line_name, record.license_plate, record.operator_ref, record.line_ref,
                       record.departure_time, record.journey_ref)].update(set(record.siri_records))

    def get_rides(self):
        for siri_ride_fields, siri_records in self._records.items():
            line_name, license_plate, operator_ref, line_ref, departure_time, journey_ref = siri_ride_fields
            yield SiriRide(line_name, license_plate, operator_ref, line_ref, departure_time, journey_ref,
                           set(siri_records))


class SiriLogParser:
    def __init__(self, rides_cache_mechanism: RidesCacheMechanism):
        self.rides_cache_mechanism = rides_cache_mechanism

    def _add_record(self, record: SiriRide):
        self.rides_cache_mechanism.add_ride(record)

    def parse_multi_gz_files(self, files_path):
        for file_path in files_path:
            self.parse_gz_file(file_path)

    def parse_gz_file(self, file_path):
        with gzip.open(file_path, mode='rt', encoding="utf8") as f:
            self.parse_csv_file(f)

    def parse_csv_file(self, f):
        """
        parsing csv lines such as:
        `2020-06-24T23:11:31,[line 290 v 5743687 oad 00:20 ea 01:05],18,10584,290,47406245,2020-06-25T00:20:00,5743687,
        2020-06-25T01:05:00,2020-06-24T04:03:35,0,0,2020-06-25,60129,2,v2`
        :param f: opened csv file
        """
        for i in csv.reader(f):
            if not i:
                continue
            record = SiriRide(line_name=i[4], license_plate=i[7], operator_ref=i[2], line_ref=i[3],
                              departure_time=datetime.fromisoformat(i[6]).time(),
                              journey_ref=i[5], siri_records={SiriRecord(
                                recorded_at=datetime.fromisoformat(i[9]).time(),
                                response_timestamp=datetime.fromisoformat(i[0]),
                                expected_arrival_time=datetime.fromisoformat(i[8]).time(),
                                current_location=GeoPoint(longitude=i[10], latitude=i[11]))})
            self._add_record(record)

        self.rides_cache_mechanism.commit()

    def get_rides(self):
        return self.rides_cache_mechanism.get_rides()

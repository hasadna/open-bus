import csv
from datetime import datetime
import gzip
from abc import ABC, abstractmethod
from collections import defaultdict

from data_stream.base_classes import SiriRide, SiriRecord, GeoPoint


class RidesCacheMechanism(ABC):
    @abstractmethod
    def add_ride(self, record: SiriRide):
        pass

    @abstractmethod
    def get_rides(self):
        pass


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
    def __init__(self, rides_cache_mechanism: InMemoryRidesCacheMechanism):
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

    def get_rides(self):
        return self.rides_cache_mechanism.get_rides()

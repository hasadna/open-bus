from abc import ABC, abstractmethod
from typing import List, Tuple
from datetime import datetime


class Serializable(ABC):
    @abstractmethod
    def to_json(self) -> dict:
        pass

    def __repr__(self):
        return str(self.__dict__)


class SiriRideAnalytics(Serializable):
    """
    TBD
    """

    def to_json(self) -> dict:
        pass


class SiriRecord(Serializable):
    def __init__(self, recorded_at, response_timestamp, expected_arrival_time, current_location):
        self.recorded_at: datetime = recorded_at
        self.response_timestamp: datetime = response_timestamp
        self.expected_arrival_time = expected_arrival_time
        self.current_location: Tuple[float, float] = current_location

    def to_json(self) -> dict:
        return dict(recordedAt=self.recorded_at.strftime("%H:%M:%S"),
                    responseTimestamp=self.response_timestamp.astimezone().isoformat(),
                    expectedArrivalTime=self.expected_arrival_time.strftime("%H:%M:%S"),
                    point=dict(type='Point', coordinates=list(self.current_location)))


class SiriRide(Serializable):
    _type = "siri_ride"

    def __init__(self, siri_ride_id, line_name, license_plate, operator_ref, line_ref, departure_time, journey_ref,
                 siri_records, siri_ride_analytics):
        self.siri_ride_id = siri_ride_id
        self.line_name = line_name
        self.license_plate = license_plate
        self.departure_time: datetime = departure_time
        self.operator_ref = operator_ref
        self.line_ref = line_ref
        self.journey_ref = journey_ref
        self.siri_records: List[SiriRecord] = siri_records
        self.siri_ride_analytics: SiriRideAnalytics = siri_ride_analytics

    def to_json(self) -> dict:
        return dict(type=self._type, id=str(self.siri_ride_id),
                    attributes=dict(lineName=self.line_name, licensePlate=self.license_plate,
                                    departureTime=self.departure_time.strftime("%H:%M:%S"), journeyRef=self.journey_ref,
                                    operatorRef=self.operator_ref, lineRef=self.line_ref,
                                    siriRecords=[i.to_json() for i in self.siri_records]))

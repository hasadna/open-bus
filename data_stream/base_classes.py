from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, time


class Serializable(ABC):
    @abstractmethod
    def to_json(self) -> dict:
        pass

    def __repr__(self):
        return str(self.__dict__)


class GeoPoint(Serializable):
    def __init__(self, longitude: float, latitude: float):
        self.longitude = longitude
        self.latitude = latitude

    def to_json(self) -> dict:
        return dict(type='Point', coordinates=[self.longitude, self.latitude])


class SiriRideAnalytics(Serializable):
    """
    TBD
    """

    def to_json(self) -> dict:
        pass


class SiriRecord(Serializable):
    def __init__(self, recorded_at: time, response_timestamp: datetime, expected_arrival_time: time,
                 current_location: GeoPoint):

        self.recorded_at: time = recorded_at
        self.response_timestamp: datetime = response_timestamp
        self.expected_arrival_time: time = expected_arrival_time
        self.current_location: GeoPoint = current_location

    def to_json(self) -> dict:
        return dict(recordedAt=self.recorded_at.strftime("%H:%M:%S"),
                    responseTimestamp=self.response_timestamp.astimezone().isoformat(),
                    expectedArrivalTime=self.expected_arrival_time.strftime("%H:%M:%S"),
                    point=self.current_location.to_json())


class SiriRide(Serializable):
    _type = "siri_ride"

    def __init__(self, siri_ride_id: int, line_name: str, license_plate: str, operator_ref: int, line_ref: int,
                 departure_time: datetime, journey_ref: int, siri_records: List[SiriRecord],
                 siri_ride_analytics: SiriRideAnalytics = None):
        """

        :param siri_ride_id:
        :param line_name:
        :param license_plate:
        :param operator_ref:
        :param line_ref:
        :param departure_time:
        :param journey_ref: The number part of trip ID. Valid value is like: 20925867. The value is reference to
               TripId at TripIdToDate.txt file at the GTFS
        :param siri_records:
        :param siri_ride_analytics:
        """
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

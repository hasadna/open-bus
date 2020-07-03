from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime, time


class Serializable(ABC):
    @abstractmethod
    def to_json(self) -> dict:  # pragma: no cover
        pass

    @staticmethod
    @abstractmethod
    def from_json(json_doc: Dict[str, Any]) -> Serializable:  # pragma: no cover
        pass

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __hash__(self):
        return hash(self.__dict__)


class DBDocument(Serializable, ABC):
    @property
    @abstractmethod
    def doc_type(self):  # pragma: no cover
        pass


class GeoPoint(Serializable):

    def __init__(self, longitude: float, latitude: float):
        assert longitude is not None
        assert latitude is not None

        self.longitude = longitude
        self.latitude = latitude

    def to_json(self) -> dict:
        return dict(type='Point', coordinates=[self.longitude, self.latitude])

    @staticmethod
    def from_json(json_doc: Dict[str, Any]) -> GeoPoint:
        return GeoPoint(*json_doc['coordinates'])


class SiriRideAnalytics(Serializable):
    """
    TBD
    """

    @staticmethod
    def from_json(json_doc: Dict[str, Any]) -> SiriRideAnalytics:  # pragma: no cover
        pass

    def to_json(self) -> dict:  # pragma: no cover
        pass


class SiriRecord(Serializable):

    def __init__(self, recorded_at: time, response_timestamp: datetime, expected_arrival_time: time,
                 current_location: GeoPoint):

        self.recorded_at: time = recorded_at.replace(microsecond=0)

        self.response_timestamp: datetime = response_timestamp.astimezone()
        self.expected_arrival_time: time = expected_arrival_time.replace(microsecond=0)
        self.current_location: GeoPoint = current_location

    def to_json(self) -> dict:
        return dict(recordedAt=self.recorded_at.strftime("%H:%M:%S"),
                    responseTimestamp=self.response_timestamp.isoformat(),
                    expectedArrivalTime=self.expected_arrival_time.strftime("%H:%M:%S"),
                    point=self.current_location.to_json())

    @staticmethod
    def from_json(json_doc: Dict[str, Any]) -> SiriRecord:
        return SiriRecord(recorded_at=datetime.strptime(json_doc.get('recordedAt'), "%H:%M:%S").time(),
                          response_timestamp=datetime.fromisoformat(json_doc.get('responseTimestamp')),
                          expected_arrival_time=datetime.strptime(json_doc.get('expectedArrivalTime'),
                                                                  "%H:%M:%S").time(),
                          current_location=GeoPoint.from_json(json_doc.get('point')))


class SiriRide(DBDocument):

    doc_type = "siri_ride"

    def __init__(self, line_name: str, license_plate: str, operator_ref: int, line_ref: int,
                 departure_time: time, journey_ref: int, siri_records: List[SiriRecord], doc_id: str = None,
                 siri_ride_analytics: SiriRideAnalytics = None):
        """

        :param doc_id:
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
        self.doc_id = doc_id
        self.line_name = line_name
        self.license_plate = license_plate
        self.departure_time: time = departure_time.replace(microsecond=0)
        self.operator_ref = int(operator_ref)
        self.line_ref = int(line_ref)
        self.journey_ref = int(journey_ref)
        self.siri_records: List[SiriRecord] = siri_records
        self.siri_ride_analytics: SiriRideAnalytics = siri_ride_analytics

    def to_json(self) -> Dict[str, Any]:
        return dict(type=SiriRide.doc_type, id=self.doc_id,
                    attributes=dict(lineName=self.line_name, licensePlate=self.license_plate,
                                    departureTime=self.departure_time.strftime("%H:%M:%S"), journeyRef=self.journey_ref,
                                    operatorRef=self.operator_ref, lineRef=self.line_ref,
                                    siriRecords=[i.to_json() for i in self.siri_records]))

    @staticmethod
    def from_json(json_doc: Dict[str, Any]) -> SiriRide:
        attributes = json_doc.get('attributes')

        return SiriRide(doc_id=json_doc.get('id'), line_name=attributes.get('lineName'),
                        license_plate=attributes.get('licensePlate'), operator_ref=attributes.get('operatorRef'),
                        line_ref=attributes.get('lineRef'),
                        departure_time=datetime.strptime(attributes.get('departureTime'), "%H:%M:%S").time(),
                        journey_ref=attributes.get('journeyRef'),
                        siri_records=[SiriRecord.from_json(i) for i in attributes.get('siriRecords')])

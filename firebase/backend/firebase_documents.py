from datetime import datetime
from google.cloud.firestore import GeoPoint
from typing import Tuple, List


class FirebaseDocument(object):
    def to_firebase_dict(self):
        raise NotImplementedError()


class Point(FirebaseDocument):
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def to_firebase_dict(self):
        return GeoPoint(self.lat, self.lon)


class SiriPoint(FirebaseDocument):
    def __init__(self, point: Point, rec_dt: datetime, pred_dt: datetime):
        """
        :param point: The geo location of the bus
        :param rec_dt: The time that the bus has been at the point
        :param pred_dt: The time siri client ask about bus location
        """
        self.rec_dt = rec_dt
        self.pred_dt = pred_dt
        self.point = point

    @staticmethod
    def from_str(line: str):
        rec_dt, lat, lon, pred_dt = line.split('|')
        rec_dt = datetime.strptime(rec_dt, '%Y-%m-%dT%H:%M:%S')
        pred_dt = datetime.strptime(pred_dt, '%Y-%m-%dT%H:%M:%S')
        point = Point(float(lat), float(lon))

        return SiriPoint(point, rec_dt, pred_dt)

    def to_firebase_dict(self):
        return dict(rec_dt=self.rec_dt, pred_dt=self.pred_dt, point=self.point.to_firebase_dict())


class SiriRide(FirebaseDocument):
    def __init__(self, route_id: int, agency_id: int, bus_id: str, planned_start_datetime: datetime,
                 route_short_name: str, stop_point_ref: Tuple[float, float], trip_id_to_date: int,
                 points: List[SiriPoint], **kwargs):
        """
        :param route_id: Identifies a route
        :param agency_id: Identifies a bus agency
        :param bus_id: Identifies vehicle
        :param planned_start_datetime: Departure time from a first stop
        :param route_short_name: Short name of a route. This will often be a short, abstract identifier like "32"
        :param stop_point_ref:
        :param trip_id_to_date:
        :param points: Realtime locations of vehicle
        :param kwargs: Other metadata
        """
        self.route_id = route_id
        self.agency_id = agency_id
        self.bus_id = bus_id
        self.planned_start_datetime = planned_start_datetime
        self.route_short_name = route_short_name
        self.stop_point_ref = stop_point_ref
        self.trip_id_to_date = trip_id_to_date
        self.points = points
        self.metadata = kwargs

    def to_firebase_dict(self):
        return dict(route_id=self.route_id, agency_id=self.agency_id, bus_id=self.bus_id,
                    planned_start_datetime=self.planned_start_datetime, route_short_name=self.route_short_name,
                    stop_point_ref=self.stop_point_ref, trip_id_to_date=self.trip_id_to_date,
                    points=[i.to_firebase_dict() for i in self.points], metadata=self.metadata)

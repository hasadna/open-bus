import datetime

##from crud_stub import CrudStub

METERS_IN_KM = 1000
SEC_IN_HOUR = 60 * 60
RECORD_BEFORE = 0
RECORD_AFTER = 1


class Record:
    def __init__(self, trip_id=None, recorded_at_time=None, vehicle_ref=None, route_offset=None, **kwd):
        self.trip_id = trip_id
        self.recorded_at_time = recorded_at_time
        self.vehicle_ref = vehicle_ref
        self.route_offset = route_offset
        self.route_offset_in_meters = None

        for k, v in kwd.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def add_route_offset_in_meters(self, max_trip_dist):
        self.route_offset_in_meters = max_trip_dist * self.route_offset

    def __eq__(self, other):
        if not isinstance(other, Record):
            return False
        elif self is other:
            return True
        else:
            return self.trip_id == other.trip_id and self.recorded_at_time == other.recorded_at_time

    def __hash__(self):
        return hash((self.trip_id, self.recorded_at_time))


class Stop:
    def __init__(self,
                 trip_id=None,
                 route_short_name=None,
                 route_id=None,
                 route_long_name=None,
                 arrival_time=None,
                 stop_id=None,
                 stop_sequence=None,
                 shape_dist_traveled=None, **kwd):

        self.trip_id = trip_id
        self.route_short_name = route_short_name
        self.route_id = route_id
        self.route_long_name = route_long_name
        self.arrival_time = arrival_time
        self.stop_id = stop_id
        self.stop_sequence = stop_sequence
        self.shape_dist_traveled = shape_dist_traveled

        for k, v in kwd.items():
            if hasattr(self, k):
                setattr(self, k, v)


class Trip:
    def __init__(self, trip_id=None, trip_date=None, crud=None, **kwd):
        self.crud = crud
        self.trip_date = trip_date
        self.trip_id = trip_id
        self.stops = []
        self.records = []
        self.real_times = []
        self.stops_with_no_realtime = []

        for k, v in kwd.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def __call__(self):
        self.run()
        return True

    def run(self):
        self._fill_()
        self._update_on_disk()
        return ({'num of real times':len(self.real_times),'errors':self.stops_with_no_realtime})

    def _fill_(self):
        self.stops = self.crud.read_stops(self.trip_id)
        self.records = list(set(self.crud.read_records_from_siri(self.trip_id, self.trip_date)))
        if not self.stops or not self.records:
            print('No values')


        self.stops.sort(key=lambda x: x.stop_sequence)
        self.records.sort(key=lambda x: x.route_offset)
        self._add_route_offset_in_meters(self.stops[-1].shape_dist_traveled)
        self._real_time()


    def _update_on_disk(self):
        self.crud.write_arrivals(self.real_times)

    def _add_route_offset_in_meters(self, max_dist):
        for record in self.records:
            record.add_route_offset_in_meters(max_dist)

    def _get_before_and_after_records(self, stop):
        # print("stops: {} records: {}".format(self.stops, self.records))
        if not self.records:
            raise ValueError("No records at all")
        shape_dist = stop.shape_dist_traveled
        for index, curr in enumerate(self.records[1:], 1):
            if curr.route_offset_in_meters > shape_dist:
                if self.records[index - 1].route_offset_in_meters <= shape_dist:
                    return self.records[index - 1], self.records[index]
                else:
                    raise ValueError('Not Found - all records occurs after stop at: {} first record at:{}'
                                     .format(shape_dist, self.records[index - 1].route_offset_in_meters))
        raise ValueError('Not Found - all records occurs before stop at: {} last record at:{}'.
                         format(shape_dist, self.records[-1].route_offset_in_meters))

    def _real_time(self):
        for stop in self.stops:
            try:
                b, a = self._get_before_and_after_records(stop)
                self.real_times.append(RealTime(b, a, stop))
            except ValueError as e:
                self.stops_with_no_realtime.append({'stop':stop,'comment':e})



class RealTime:
    def __init__(self, before, after, stop):
        self.records = (before, after)
        self.stop = stop
        self.speed = None
        self.real_time = None
        self.calc()

    def calc(self):
        self.speed = self._calc_speed_between_records()
        distance = self._calc_distance()
        self.real_time = self._calc_arrival_time(distance)

    def _calc_speed_between_records(self):
        b, a = self.records
        seconds_between_records = (a.recorded_at_time - b.recorded_at_time).total_seconds()
        distance_between_records = float(a.route_offset_in_meters - b.route_offset_in_meters)
        return distance_between_records / seconds_between_records / METERS_IN_KM * SEC_IN_HOUR

    def _calc_distance(self):
        return float(self.stop.shape_dist_traveled - self.records[RECORD_BEFORE].route_offset_in_meters) / METERS_IN_KM

    def _calc_arrival_time(self, distance):
        time_in_sec = distance / self.speed * SEC_IN_HOUR
        return self.records[RECORD_BEFORE].recorded_at_time + datetime.timedelta(seconds=time_in_sec)

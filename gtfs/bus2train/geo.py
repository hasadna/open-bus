"""Function and classes related to geography and site."""

import math
import collections
from csv import DictReader
import logging

try:
    import shapefile
except ImportError:
    logging.getLogger(__name__).debug('Cannot find shapefile module. Functions that depend on it will fail')

# earth radius in meters
R_EARTH = (6378137.0 + 6356752.3141) / 2.0


class GeoPoint:
    """A WGS84 coordinate"""

    def __init__(self, lat, long):
        """Initializes the object from latitude and longitude

        :param lat: String | number
        :param long: String | number
        :return: None
        """

        self.lat = float(lat)
        self.long = float(long)
        self.cartesian = None

    @classmethod
    def from_tuple(cls, t):
        """Generates a GeoPoint from a tuple (latitude, longitude)

        :param t: (float, float)    # (latitude, longitude)
        :return:GeoPoint
        """
        return cls(t[0], t[1])

    @classmethod
    def from_cartesian(cls, cartesian):
        """Converts a CartesianPoint into a GeoPoint.

        :param cartesian: CartesianPoint
        :return: GeoPoint
        """
        z = cartesian.z
        y = cartesian.y
        x = cartesian.x
        theta = math.asin(z / R_EARTH)
        phi = math.atan2(y, x)
        lat = math.degrees(theta)
        lon = math.degrees(phi)
        if lon < 0:
            lon += 360
        return cls(lat, lon)

    def __eq__(self, other):
        return self.lat == other.lat and self.long == other.long

    def __repr__(self):
        return '(' + str(self.lat) + ',' + str(self.long) + ')'

    def __hash__(self):
        return (self.lat, self.long).__hash__()

    @property
    def ns(self):
        """ns (north-south) is an alias for lat"""
        return self.lat

    @property
    def we(self):
        """we (west-east) is an alias for long"""
        return self.long

    def point_at_distance(self, distance, heading):
        """Returns a another GeoPoint at the given distance and heading

        :param distance: float  # in meters
        :param heading: float   # in degrees
        :return: GepPoint
        """
        distance_rad = distance / R_EARTH
        heading_rad = math.radians(heading)
        return self.__spherical_between(math.radians(self.lat), math.radians(self.long), distance_rad, heading_rad)

    def heading_to(self, p1):
        """Calculate the heading from current point to p1.

        :param p1: GeoPoint
        :return: float  # in degrees
        """
        # Turn them all into radians
        phi1 = math.radians(self.lat)
        lambda0 = math.radians(self.long)
        phi = math.radians(p1.lat)
        lambda_ = math.radians(p1.long)

        ldiff = lambda_ - lambda0
        cosphi = math.cos(phi)

        bearing = math.atan2(cosphi * math.sin(ldiff),
                             (math.cos(phi1) * math.sin(phi) - math.sin(phi1) * cosphi * math.cos(ldiff)))
        bearing_deg = math.degrees(bearing)
        if bearing_deg < 0:
            bearing_deg += 360

        return bearing_deg

    def distance_to(self, p1):
        """Calculates the distance from the current point to p1

        :param p1: GeoPoint
        :return: int # in meters
        """
        # due to rounding errors the actual function can return non-zero distance for the same point!
        if self.round() == p1.round():
            return 0
        from_theta = float(self.lat) / 360.0 * 2.0 * math.pi
        from_landa = float(self.long) / 360.0 * 2.0 * math.pi
        to_theta = float(p1.lat) / 360.0 * 2.0 * math.pi
        to_landa = float(p1.long) / 360.0 * 2.0 * math.pi
        tmp = math.sin(from_theta) * math.sin(to_theta) + math.cos(from_theta) * math.cos(to_theta) * math.cos(
            to_landa - from_landa)
        # if I don't round the number, ValueError: math domain error may occur
        return math.acos(round(tmp, 15)) * R_EARTH

    # see http://rbrundritt.spaces.live.com/blog/cns!E7DBA9A4BFD458C5!280.entry
    # returns the matching coordinate in the cartesian 3D space with origin = earth center.
    # used to calculate distance between point and line
    def to_cartesian(self):
        """Convert the current point to a cartesian point

        :return: CartesianPoint
        """

        if self.cartesian is None:
            theta = math.radians(self.lat)
            phi = math.radians(self.long)
            x = R_EARTH * math.cos(theta) * math.cos(phi)
            y = R_EARTH * math.cos(theta) * math.sin(phi)
            z = R_EARTH * math.sin(theta)
            self.cartesian = CartesianPoint(x, y, z)
        return self.cartesian

    def round(self):
        """find the a GeoPoint with the coordinates rounded to 5 decimal places

        :return: GeoPoint
        """
        return GeoPoint(round(self.lat, 5), round(self.long, 5))

    @staticmethod
    def __spherical_between(phi1, lambda0, c, az):
        cos_ph1 = math.cos(phi1)
        sun_ph1 = math.sin(phi1)
        cos_az = math.cos(az)
        sin_az = math.sin(az)
        sin_c = math.sin(c)
        cos_c = math.cos(c)

        lat_rad = math.asin(sun_ph1 * cos_c + cos_ph1 * sin_c * cos_az)
        long_rad = math.atan2(sin_c * sin_az, cos_ph1 * cos_c - sun_ph1 * sin_c * cos_az) + lambda0
        return GeoPoint(math.degrees(lat_rad), math.degrees(long_rad))

    @staticmethod
    def west_to_east(d1, d2):
        """Returns the two input coordinates in pair p, so that p[0] is the western most coordinates.

        :param d1: float   # a longitude
        :param d2: float   # a longitude
        :return: (float, float)   #(d1, d2) if d1 is the western most, (d2, d1) otherwise
        """
        e1 = max(d1, d2)
        e2 = min(d1, d2)
        if e1 - e2 < 180:
            return e2, e1
        return e1, e2


class CartesianPoint(collections.namedtuple('CartesianPoint', 'x y z')):
    """A Geographic coordinate represented in (x,y,z), where (0,0,0) is the center of the earth"""

    @classmethod
    def from_tuple(cls, t):
        """Factory method: create a Cartesian point from an (x,y,z) tuple

        :param t: (float, float, float)  # x, y, z
        :return: CartesianPoint
        """
        return cls(t[0], t[1], t[2])

    def distance_to(self, other):
        """calculate distance to the other point

        :param other: CartesianPoint | GeoPoint     # or something else that defines properties x, y, z
        :return: float  # the distance from this point to the other point
        """
        if type(other) == GeoPoint:
            other = other.to_cartesian()
        d0 = self.x - other.x
        d1 = self.y - other.y
        d2 = self.z - other.z

        return math.sqrt(d0 * d0 + d1 * d1 + d2 * d2)


class GeoBox:
    """A geographical rectangle"""
    # could be init with center + size or by a set of points
    def __init__(self, center, size=0):
        if size == 0:
            self.north_west = self.south_east = center
        else:
            north = center.get_point_at_distance(size / 2, 0).ns()
            west = center.get_point_at_distance(size / 2, 270).we()
            self.north_west = GeoPoint(north, west)
            south = center.get_point_at_distance(size / 2, 180).ns()
            east = center.get_point_at_distance(size / 2, 90).we()
            self.south_east = GeoPoint(south, east)

    @classmethod
    def from_points(cls, points, margin_in_meters=0):
        """Generates a minimal GeoBox that contains all the specified points.

        GeoBox is the minimal box that is at least margin_in_meters away from all points.

        :param points: list[GeoPoint]   # The points to include
        :param margin_in_meters:        # the minimal distance of the box boundaries from each point
        :return:GeoBox
        """
        box = cls(points[0])
        for pt in points[1:]:
            box.expand_to_contain(pt)
        box.expand_by_constant(margin_in_meters)
        return box

    @classmethod
    def from_boxes(cls, boxes):
        """Generates a minimal GeoBox that contains all the specified points (minimal superset)

        :param boxes: list[GeoBox]  # the boxes to include
        :return: GeoBox
        """
        points = [box.north_west for box in boxes] + [box.south_east for box in boxes]
        return cls.from_points(points)

    @property
    def west(self):
        """Returns the western-most longitude (x) value of this box

        :return: float
        """
        return self.north_west.we

    @property
    def east(self):
        """Returns the eastern-most longitude (x) value of this box

        :return: float
        """
        return self.south_east.we

    @property
    def north(self):
        """Returns the northern-most latitude (y) value of this box

        :return: float
        """
        return self.north_west.ns

    @property
    def south(self):
        """Returns the southern-most latitude (y) value of this box

        :return: float
        """
        return self.south_east.ns

    def __repr__(self):
        return '[' + repr(self.north_west) + ' : ' + repr(self.south_east) + ']'

    def __eq__(self, other):
        return self.south_east == other.south_east and self.north_west == other.north_west

    def __contains__(self, item):
        lat = item.lat
        long = item.long
        if self.south_east.lat <= lat <= self.north_west.lat:
            if self.west <= self.east:  # normal situation
                return self.west <= long <= self.east
            else:  # across prime meridian
                return self.east <= long <= self.west
        else:
            return False

    def expand_to_contain(self, point):
        """If the given point isn't inside this box, expand the box boundaries to contain it

        :param point: the point to add
        :return: None
        """
        if self.north_west is None:
            self.north_west = self.south_east = point
        else:
            north = max(self.north_west.lat, point.lat)
            south = min(self.south_east.lat, point.lat)

            west, _ = GeoPoint.west_to_east(self.north_west.long, point.long)
            _, east = GeoPoint.west_to_east(self.south_east.long, point.long)

            if west != self.north_west.we and east != self.south_east.we:
                raise ValueError('Box size expanded over 180 degrees')

            self.north_west = GeoPoint(north, west)
            self.south_east = GeoPoint(south, east)

    def expand_by_constant(self, margin):
        """enlarge the bounding box by a constant size to all directions.

        :param margin: int | float   # margin to add, in meters
        :return: None
        """
        diagonal_margin = math.sqrt(2 * margin * margin)
        self.north_west = self.north_west.point_at_distance(diagonal_margin, 315)
        self.south_east = self.south_east.point_at_distance(diagonal_margin, 135)

        west, east = GeoPoint.west_to_east(self.north_west.we, self.south_east.we)
        if west != self.north_west.we:
            raise ValueError('Error expanding by constant: box size exceeded 180 degrees')


class GeoLineSegment:
    """A geographical line segment, defined by its start and end points"""

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.length = start.distance_to(end)
        self.heading = start.heading_to(end)

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __repr__(self):
        return '(' + repr(self.start) + ' : ' + repr(self.end) + ')'

    def heading_difference(self, other_heading):
        """Returns the difference between the heading of the current segment and other_heading

        :param other_heading: float
        :return: float
        """
        diff = abs(self.heading - other_heading)
        if diff > 180:
            diff = 360 - diff
        return diff

    @property
    def middle(self):
        """Returns the GeoPoint in the middle of this segment

        :return: GeoPoint
        """
        return self.start.point_at_distance(self.length / 2, self.heading)


class GeoPolyline:
    """Represents a multiple-point geographic line"""

    def __init__(self, parts):
        """Initialize a polyline from GeoLineSegment objects

        :param parts: list[geo.GeoLineSegment]      # parts of the road
        :return: None
        """
        self.parts = parts
        self.length = sum([p.length for p in parts])

    def __repr__(self):
        return "<GeoPolyline from %s to %s, length %.02f>" % (self.parts[0].start, self.parts[-1].end, self.length)

    @classmethod
    def from_points(cls, points):
        """Generates a GeoPolyline from the given points

        :param points: list[GeoPoint]
        :return: GeoPolyline
        """
        return cls(SiteLoader.points_to_pairs(points))

    def offset_from_start(self, part):
        """Finds the distance of the start of part from the start of the polyline, when iterating over the polyline.
        Part must be one of the parts of the polyline (otherwise exception will be raised)

        :param part: GeoLineSegment
        :return: float
        """
        index = self.parts.index(part)
        return sum([p.length for p in self.parts[:index]])

    def point_and_heading_at_offset(self, offset_in_meters):
        """Returns point at distance offset_in_meters from the start of the polyline, and the heading at that point"""
        current_offset_from_start = 0
        for part in self.parts:
            if current_offset_from_start + part.length >= offset_in_meters:  # the point is somewhere along this part
                return part.start.point_at_distance(offset_in_meters - current_offset_from_start), part.heading
            current_offset_from_start += part.length

        raise ValueError('offset_in_meters must be <= %f' % self.length)

    @property
    def middle(self):
        """Returns the point at the middle of the polyline, and the heading at that point"""
        return self.point_and_heading_at_offset(self.length/2)

    @staticmethod
    def line_length(points):
        line = GeoPolyline.from_points(points)
        return line.length


class ShapeFile:
    """A collection of static method related to loading data from shape files"""

    @staticmethod
    def shape_lines_reader(file_name, fields_to_export=None):
        """A generator that returns pairs of attributes and point list for features in a shape file.

        If fields_to_export is None, all attributes will be exported.

        :param file_name: String    # shape file to read (without suffix
        :param fields_to_export: list[String]  # list of attributes to export from the shape file, or None
        :return: a generator. Each call to the generator returns a pair:
            - a dictionary from field name to field value
            - a list of GeoPoint objects
        """
        # read the roads shape file
        roads_sf = shapefile.Reader(file_name)

        # get the fields in fields available
        # returns a list of tuples that look like: ['RoadID', 'N', 9, 0]
        # for some reason the first field (DeletionFlag) has to be skipped
        shape_field_list = [x[0] for x in roads_sf.fields][1:]

        # transform the list of field names to a list of field indexes
        fields_to_index = {}
        for i, field_name in enumerate(shape_field_list):
            fields_to_index[field_name] = i

        for shapeRecord in roads_sf.shapeRecords():
            if fields_to_export:
                record = dict([(name, shapeRecord.record[fields_to_index[name]]) for name in fields_to_export])
            else:
                record = dict([(name, shapeRecord.record[fields_to_index[name]]) for name in shape_field_list])
            points = [GeoPoint(lat, long) for long, lat in shapeRecord.shape.points]
            yield record, points

    @staticmethod
    def read_shape_lines(file_name, id_field_name, fields_to_export=[]):
        """A function that returns a map from shape id to a pair containing its attributes and the shape itself

        :param file_name: name of file to read from, without .shp extension
        :param id_field_name: name of the attribute to use as id
        :param fields_to_export: list of attributes to export from the shape file. If None, all attributes are exported.
        :return:
        """
        result = {}
        if id_field_name not in fields_to_export:
            fields_to_export = [id_field_name] + fields_to_export
        for record, points in ShapeFile.shape_lines_reader(file_name, fields_to_export):
            result[record[id_field_name]] = record, points
        return result

    @staticmethod
    def export_shape_lines(shape_file_name, attrs_file, xy_file, id_field_name, fields_to_export=[]):
        # put id field first!
        fields_to_export = [id_field_name] + [field for field in fields_to_export if field != id_field_name]
        with open(attrs_file, 'w') as af, open(xy_file, 'w') as xyf:
            af.write('\t'.join(fields_to_export) + '\n')
            xyf.write('Id' + '\t' + 'Long' + '\t' + 'Lat' + '\t' + 'CooIndex' + '\n')
            for record, points in ShapeFile.shape_lines_reader(shape_file_name, fields_to_export):
                id_val = record[id_field_name]
                attrs_fields = [str(record[field_name]) for field_name in fields_to_export]
                af.write('\t'.join(attrs_fields) + '\n')
                for index, point in enumerate(points):
                    xy_fields = [str(id_val), format(point.long, '.05f'), format(point.lat, '.05f'), str(index)]
                    xyf.write('\t'.join(xy_fields) + '\n')


class GeoGrid:
    def __init__(self, box, size):
        self.box = box
        self.size = size

    def get_cell(self, point):
        west = self.box.west
        east = self.box.east
        south = self.box.south
        north = self.box.north
        x = abs((point.long - west) / (east - west) * self.size)
        y = abs((point.lat - south) / (north - south) * self.size)
        return int(x), int(y)

    def get_cell_center(self, x, y):
        x_cell_size = (self.box.east - self.box.west) / (self.size + 1)
        long = x * x_cell_size + x_cell_size / 2
        y_cell_size = (self.box.north - self.box.south) / (self.size + 1)
        lat = y * y_cell_size + y_cell_size / 2
        return GeoPoint(lat, long)



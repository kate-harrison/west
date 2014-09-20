from protected_entity import ProtectedEntity
from shapely.geometry import Polygon


class ProtectedEntityRadioAstronomySite(ProtectedEntity):
    """
    Radioastronomy site.
    """
    # TODO: do RAS rectangles need to be protected within the rectangle or within 2.4 km of the rectangle?

    _required_properties = ["_latitude", "_longitude", "_channel", "_is_point"]

    def __init__(self, container, region, latitude, longitude, channel, name, is_point, latitude_deviation=None, longitude_deviation=None):
        super(ProtectedEntityRadioAstronomySite, self).__init__(region, container, latitude, longitude)

        self._channel = channel

        self._is_point = is_point
        if not is_point and (latitude_deviation is None or longitude_deviation is None):
            self.log.error("Non-point radio astronomy site specified but missing a latitude/longitude deviation value.")

        self._latitude_deviation = latitude_deviation
        self._longitude_deviation = longitude_deviation

        self._name = name

        # Must come after assignment of deviations
        if not self.is_point():
            self._create_new_bounding_box()

        self._log_error_if_necessary_data_missing()

    def to_string(self):
        output = "%s\tLatitude: %.2f\t\tLongitude: %.2f" % (str(self._name).ljust(30), self._latitude, self._longitude)
        if self._is_point:
            output += "\t(point)"
        else:
            output += "\t(rectangle; deviations: %.2f, %.2f)" % (self._latitude_deviation, self._longitude_deviation)
        return output

    def add_to_kml(self, kml):
        if self.is_point():
            point = kml.newpoint()
            point.name = str(self._name)
            point.description = """
            Name: %s
            Channel: %d
            Latitude: %.2f
            Longitude: %.2f
            """ % (self._name, self.get_channel(), self.get_latitude(), self.get_longitude())
            point.coords = [(self.get_longitude(), self.get_latitude())]
            return point
        else:
            poly = kml.newpolygon()
            poly.name = str(self._name)

            latlon_coordinates = self.get_coordinates()
            lonlat_coordinates = [ (lon, lat) for (lat, lon) in latlon_coordinates]
            lonlat_coordinates.append(lonlat_coordinates[0])
            poly.outerboundaryis.coords = lonlat_coordinates

            poly.description = """
            Name: %s
            Channel: %d
            Center latitude: %.2f (deviation: %2.2f decimal degrees)
            Center longitude: %.2f (deviation: %2.2f decimal degrees)
            """ % (self._name, self.get_channel(), self.get_latitude(), self._latitude_deviation, self.get_longitude(),
                   self._longitude_deviation)
            return poly

    def is_point(self):
        """
        Some RAS sites are points and others are polygons. This function differentiates them.

        :return: True if the radioastronomy site is a point; False otherwise
        :rtype: bool
        """
        return self._is_point

    def get_coordinates(self):
        if self._is_point:
            return self.get_location()
        else:
            return [
                (self._latitude + self._latitude_deviation, self._longitude + self._longitude_deviation),
                (self._latitude + self._latitude_deviation, self._longitude - self._longitude_deviation),
                (self._latitude - self._latitude_deviation, self._longitude - self._longitude_deviation),
                (self._latitude - self._latitude_deviation, self._longitude + self._longitude_deviation)
            ]

    def get_shapely_polygon(self):
        if self._is_point:
            return None

        coordinates = self.get_coordinates()
        coordinates.append(coordinates[0])
        return Polygon(coordinates)

    def _create_new_bounding_box(self):
        """
        Creates an alternative bounding box for non-point entries. Note that in this case the bounding box is the same
        as the protected region (both rectangles).

        :return: None
        """
        if self.is_point():
            return
        else:
            bb = {'min_lat': float('inf'),
                  'max_lat': -float('inf'),
                  'min_lon': float('inf'),
                  'max_lon': -float('inf')
            }

            for (lat, lon) in self.get_coordinates():
                if lat < bb['min_lat']:
                    bb['min_lat'] = lat
                if lat > bb['max_lat']:
                    bb['max_lat'] = lat
                if lon < bb['min_lon']:
                    bb['min_lon'] = lon
                if lon > bb['max_lon']:
                    bb['max_lon'] = lon

            self._protected_bounding_box = bb

    def location_in_protected_polygon(self, device_location):
        if self.is_point():
            return False
        else:
            (lat, lon) = device_location
            return (
                (self._latitude - self._latitude_deviation <= lat <= self._latitude + self._latitude_deviation)
                and
                (self._longitude - self._longitude_deviation <= lon <= self._longitude + self._longitude_deviation)
            )

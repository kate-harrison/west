from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger
from geopy.distance import VincentyDistance
from protected_entities import ProtectedEntities
from geopy import Point


class ProtectedEntity(object):
    """Generic protected entity."""
    __metaclass__ = ABCMeta

    required_properties = ["latitude", "longitude"]

    def __init__(self, region, container, latitude, longitude):
        self.log = getModuleLogger(self)
        self.region = region

        self.container = container
        if not isinstance(container, ProtectedEntities):
            # TODO: raise an exception?
            self.log.error("Container is not a ProtectedEntities instance: got %s instead." % container.__class__.__name__)

        self.latitude = latitude
        self.longitude = longitude

        self._create_bounding_box()

    def log_error_if_necessary_data_missing(self):
        """Checks for the existence and initialization of all required
        properties. Logs errors for all that are missing.

        Note: this only checks for the most essential data."""
        for property in self.required_properties:
            if not hasattr(self, property):
                self.log.error("Missing required property: ", property)

            if getattr(self, property) is None:
                self.log.error("Required property %s has value None" % property)


    def get_location(self):
        """
        :return: (latitude, longitude) in decimal degrees
        :rtype: tuple of floats
        """
        try:
            return (self.latitude, self.longitude)
        except Exception as e:
            self.log.error("Missing either latitude or longitude for this "
                           "protected entity")
            return None

    def get_latitude(self):
        """
        :return: the latitude of the protected entity in decimal degrees
        :rtype: float
        """
        return self.latitude

    def get_longitude(self):
        """
        :return: the longitude of the protected entity in decimal degrees
        :rtype: float
        """
        return self.longitude

    def get_channel(self):
        """
        Returns None if channel is not an attribute of the ProtectedEntity.

        :return:
        """
        if hasattr(self, "channel"):
            return self.channel
        else:
            return None

    def get_center_frequency(self):
        """
        Returns None if channel is not an attribute of the ProtectedEntity.

        :return: the center frequency of the ProtectedEntity in MHz
        :rtype: float
        """
        channel = self.get_channel()
        if channel is None:
            return None
        else:
            return self.region.get_center_frequency(channel)

    @abstractmethod
    def add_to_kml(self, kml):
        """

        :param kml:
        :return:
        """
        return

    def _create_bounding_box(self):
        bb = {'min_lat': float('inf'),
              'max_lat': -float('inf'),
              'min_lon': float('inf'),
              'max_lon': -float('inf')
        }

        location = Point(self.latitude, self.longitude)
        for bearing in [0, 90, 180, 270, 360]:
            destination = VincentyDistance(kilometers=self.container.get_max_protected_radius_km()).destination(location, bearing)
            lat, lon = destination.latitude, destination.longitude
            if lat < bb['min_lat']:
                bb['min_lat'] = lat
            if lat > bb['max_lat']:
                bb['max_lat'] = lat
            if lon < bb['min_lon']:
                bb['min_lon'] = lon
            if lon > bb['max_lon']:
                bb['max_lon'] = lon

        self.protected_bounding_box = bb

    def get_bounding_box(self):
        return self.protected_bounding_box

    def location_in_bounding_box(self, location):
        (lat, lon) = location
        bb = self.get_bounding_box()
        return (bb['min_lat'] <= lat <= bb['max_lat']) and (bb['min_lon'] <= lon <= bb['max_lon'])

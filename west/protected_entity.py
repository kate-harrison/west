from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger
from geopy.distance import VincentyDistance
from protected_entities import ProtectedEntities
from geopy import Point


class ProtectedEntity(object):
    """Generic protected entity."""
    __metaclass__ = ABCMeta

    _required_properties = ["_latitude", "_longitude"]

    def __init__(self, region, container, latitude, longitude):
        self.log = getModuleLogger(self)
        self._region = region

        self.container = container
        if not isinstance(container, ProtectedEntities):
            # TODO: raise an exception?
            self.log.error("Container is not a ProtectedEntities instance: "
                           "got %s instead." % container.__class__.__name__)

        self._latitude = latitude
        self._longitude = longitude

        self._create_bounding_box()

    def _log_error_if_necessary_data_missing(self):
        """Checks for the existence and initialization of all required
        properties. Logs errors for all that are missing.

        Note: this only checks for the most essential data."""
        for property in self._required_properties:
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
            return (self._latitude, self._longitude)
        except Exception as e:
            self.log.error("Missing either latitude or longitude for this "
                           "protected entity")
            return None

    def get_latitude(self):
        """
        :return: the latitude of the protected entity in decimal degrees
        :rtype: float
        """
        return self._latitude

    def get_longitude(self):
        """
        :return: the longitude of the protected entity in decimal degrees
        :rtype: float
        """
        return self._longitude

    def get_channel(self):
        """
        The channel on which the ProtectedEntity operates.

        Returns None if channel is not an attribute of the ProtectedEntity.
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
            return self._region.get_center_frequency(channel)

    @abstractmethod
    def add_to_kml(self, kml):
        """
        Add the protected entity to a KML object for display in e.g. Google Earth.

        :param kml: KML object to be modified
        :type kml: :class:`simplekml.Kml`
        :return: the object describing this ProtectedEntity in the KML (e.g. \
                for attribute modification)
        :rtype: :class:`simplekml.Point` or :class:`simplekml.Polygon`
        """
        return

    def _create_bounding_box(self):
        """
        Generate a bounding box for the ProtectedEntity. The width and height
        are set by
        :meth:`protected_entities.ProtectedEntities.get_max_protected_radius_km`.
        """
        bb = {'min_lat': float('inf'),
              'max_lat': -float('inf'),
              'min_lon': float('inf'),
              'max_lon': -float('inf')
             }

        location = Point(self._latitude, self._longitude)
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

        self._protected_bounding_box = bb

    def get_bounding_box(self):
        """
        Retrieve the bounding box for the ProtectedEntity. See
        :meth:`location_in_bounding_box` for more details.

        A bounding box is a dictionary with four keys: min_lat, max_lat,
        min_lon, max_lon. Each will give a coordinate in decimal degrees.
        """
        return self._protected_bounding_box

    def location_in_bounding_box(self, location):
        """
        Helper function to quickly identify if the ProtectedEntity is
        potentially protected. This function is faster than an actual
        protection test because it compares a few floats rather than
        computing distance, (potentially) propagation, etc.

        The width and height are set by
        :meth:`protected_entities.ProtectedEntities.get_max_protected_radius_km`.

        :param location: (latitude, longitude) in decimal degrees
        :type location: tuple of floats
        :return: True if the location is inside the bounding box; False otherwise
        :rtype: bool
        """
        (lat, lon) = location
        bb = self.get_bounding_box()
        return (bb['min_lat'] <= lat <= bb['max_lat']) and (bb['min_lon'] <=
                                                            lon <= bb['max_lon'])

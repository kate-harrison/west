from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger
from protected_entities import ProtectedEntities


class ProtectedEntity(object):
    """Generic protected entity."""
    __metaclass__ = ABCMeta

    required_properties = ["latitude", "longitude"]

    def __init__(self, region):
        self.log = getModuleLogger(self)
        self.region = region


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


class ProtectedEntityPLMRS(ProtectedEntity):

    required_properties = ["latitude", "longitude", "channel", "is_metro"]

    def __init__(self, container, region, latitude, longitude, channel, is_metro, description=None):
        super(ProtectedEntityPLMRS, self).__init__(region)

        self.container = container
        if not isinstance(container, ProtectedEntities):
            # TODO: raise an exception?
            self.log.error("Container is not a ProtectedEntities instance: got %s instead." % container.__class__.__name__)
        self.latitude = latitude
        self.longitude = longitude
        self.channel = channel
        self._is_metro = is_metro
        self._description = description

    def get_location(self):
        return (self.latitude, self.longitude)

    def get_channel(self):
        return self.channel

    def is_metro(self):
        return self._is_metro

    def to_string(self):
        output = "PLMRS protection at (%.2f, %.2f) on channel %d" % (self.latitude, self.longitude, self.channel)
        if self.is_metro():
            output += " (metro)"
        else:
            output += " (non-metro)"

        return output

    def add_to_kml(self, kml):
        point = kml.newpoint()
        point.name = str(self._description)
        if self.is_metro():
            is_metro_str = "yes"
        else:
            is_metro_str = "no"
        point.description = """
        Channel: %d
        Metropolitan area: %s
        Latitude: %.2f
        Longitude: %.2f
        """ % (self.get_channel(), is_metro_str, self.get_latitude(), self.get_longitude())
        point.coords = [(self.get_longitude(), self.get_latitude())]
        return point

    # @abstractmethod
    # def is_protected(self, lat, lon, channel=None):
    #     """Returns a boolean specifying whether or not the entity is afforded protection at the specified location.
    #     :param lat:
    #     :param long:
    #     :return:
    #     """
    #     return
    #
    # @abstractmethod
    # def might_be_protected(self, lat, lon, channel=None):
    #     """Returns True if the entity might be protected at the specified location. This
    #     function should be fairly inexpensive to execute (in comparison to is_protected)."""
    #     return
    #
    # @abstractmethod
    # def allowed_power_level(self, lat, lon, channel=None, device=None):
    #     """Returns the allowed power level (in Watts) assuming this entity is the only one afforded protection.
    #     :param lat:
    #     :param long:
    #     :param channel:
    #     :return:
    #     """
    #     return
    #
    # @abstractmethod
    # def channel_within_influence(self, channel):
    #     """Returns True if entity has influence over the specified channel."""
    #     return

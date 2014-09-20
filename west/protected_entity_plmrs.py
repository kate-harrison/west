from protected_entity import ProtectedEntity
from protected_entities import ProtectedEntities

class ProtectedEntityPLMRS(ProtectedEntity):

    _required_properties = ["_latitude", "_longitude", "_channel", "_is_metro"]

    def __init__(self, container, region, latitude, longitude, channel, is_metro, description=None):
        super(ProtectedEntityPLMRS, self).__init__(region, container, latitude, longitude)

        self._channel = channel
        self._is_metro = is_metro
        self._description = description

        self._log_error_if_necessary_data_missing()

    def get_location(self):
        return self._latitude, self._longitude

    def get_channel(self):
        return self._channel

    def is_metro(self):
        return self._is_metro

    def to_string(self):
        output = "PLMRS protection at (%.2f, %.2f) on channel %d" % (self._latitude, self._longitude, self._channel)
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

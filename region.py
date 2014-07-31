from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger
from protected_entities import ProtectedEntitiesDummy


class Region(object):
    """Region"""
    __metaclass__ = ABCMeta

    def __init__(self, simulation):
        self.log = getModuleLogger(self)
        self.simulation = simulation

        self._boundary = None

        self.protected_entities = {}
        self._load_protected_entities()

        self._load_population()
        self._load_terrain()
        # self._load_boundary()
        self._load_economic_data()

    # @abstractmethod
    # def location_is_protected(self, location, channel=None):
    #     """Returns True if the location is protected (i.e. not whitespace) by """
    #     return

    # @abstractmethod
    def location_is_in_region(self, location):
        """Returns True if the location is within the region and False
        otherwise."""
        if self._boundary is None:
            self._load_boundary()
        return self._boundary.location_inside_boundary(location)

    @abstractmethod
    def _get_boundary_class(self):
        """Returns the class to be used as the boundary of the region."""
        pass

    # @abstractmethod
    # def supported_protected_entity_types(self):
    #     """Returns a list of protected entities that are supported."""
    #     return

    @abstractmethod
    def _load_protected_entities(self):
        pass



    def _load_population(self): # TODO: write this function
        pass
    def _load_terrain(self):    # TODO: write this function
        pass
    def _load_boundary(self):   # TODO: write this function
        boundary_class = self._get_boundary_class()
        self._boundary = boundary_class(self.simulation)
    def _load_economic_data(self):  # TODO: write this function
        pass





    def get_protected_entities_of_type(self, entity_type):
        if entity_type in self.protected_entities:
            return self.protected_entities[entity_type]
        else:
            self.log.info("Using fallthrough protected entity for type %s" %
                          entity_type)
            return ProtectedEntitiesDummy()

    @abstractmethod
    def get_tvws_channel_list(self):
        """Returns a list of the channels which are considered TVWS."""
        return

    @abstractmethod
    def get_portable_tvws_channel_list(self):
        """Returns a list of channels which are considered TVWS for portable devices."""
        return

    @abstractmethod
    def get_channel_list(self):
        """Returns a list of the channels which should be considered."""
        return

    @abstractmethod
    def get_frequency_bounds(self, channel):
        """Get the (low, high) frequency bounds (in MHz) for the specified channel. Returns (None, None) if the channel
        is not supported."""
        return

    @abstractmethod
    def get_channel_width(self):
        """Get the channel width in Hz."""
        return


    def is_valid_channel(self, channel):
        return channel in self.get_channel_list()

    def is_valid_tvws_channel(self, channel):
        return channel in self.get_tvws_channel_list()

    def get_center_frequency(self, channel):
        """List the center frequency (in MHz) for the specified channel."""
        (low, high) = self.get_frequency_bounds(channel)
        return (low + high)/2.0


class SuperRegion(Region):
    """This class allows a user to combine multiple regions into one."""
    pass

    # TODO: implement SuperRegions

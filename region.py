from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger
from protected_entities import ProtectedEntitiesDummy


class Region(object):
    """Region"""
    __metaclass__ = ABCMeta

    def __init__(self, simulation=None):
        self.log = getModuleLogger(self)
        self.simulation = simulation

        self._boundary = None

        self.protected_entities = {}
        self._load_protected_entities()

        self._load_population()
        self._load_terrain()
        # self._load_boundary()
        self._load_economic_data()

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

    def _load_boundary(self):
        boundary_class = self._get_boundary_class()
        self._boundary = boundary_class(self.simulation)

    def _load_economic_data(self):  # TODO: write this function
        pass

    def get_protected_entities_of_type(self, protected_entities_type, use_fallthrough_if_not_found=False):
        """

        :param protected_entities_type: the type of protected entity (e.g. \
          :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`). Note that the base class should be used
          rather than a particular subclass.
        :type protected_entities_type: class object
        :param use_fallthrough_if_not_found: if True, returns a :class:`ProtectedEntitiesDummy` if the entity type is \
          not found. If False, a TypeError will be raised instead.
        :return:
        """
        if protected_entities_type in self.protected_entities:
            return self.protected_entities[protected_entities_type]
        elif use_fallthrough_if_not_found:
            self.log.info("Using fallthrough protected entity for type %s" %
                          protected_entities_type)
            return ProtectedEntitiesDummy(None, None)
        else:
            raise TypeError("The specified type (%s) does not exist in this Region's set of protected entities."
                            % protected_entities_type.__name__)

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

    def replace_protected_entities(self, protected_entities_type, new_protected_entities):
        """
        Raises a TypeError if the entity type is not protected by the Region or if ``new_protected_entities`` is not an
        instance of a subclass of ``protected_entities_type``.

        :param protected_entities_type: the type of protected entity (e.g. \
          :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`). Note that the base class should be used
          rather than a particular subclass.
        :type protected_entities_type: class object
        :param new_protected_entities: object containing the protected entities to be used
        :type new_protected_entities: :class:`protected_entities.ProtectedEntities`
        """
        if protected_entities_type not in self.protected_entities:
            raise TypeError("The specified type (%s) does not exist in this Region's set of protected entities."
                            % protected_entities_type.__name__)

        if not isinstance(new_protected_entities, protected_entities_type):
            raise TypeError("New ProtectedEntities object (%s) is not actually of the declared type (%s)."
                            % (str(new_protected_entities), protected_entities_type.__name__))

        self.protected_entities[protected_entities_type] = new_protected_entities


class SuperRegion(Region):
    """This class allows a user to combine multiple regions into one."""
    pass

    # TODO: implement SuperRegions

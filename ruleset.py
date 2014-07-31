from abc import ABCMeta, abstractmethod
# from doc_inherit import doc_inherit
from protected_entity_tv_station import ProtectedEntityTVStation
from custom_logging import getModuleLogger
from propagation_model_free_space import PropagationModelFreeSpace
from protected_entities_tv_stations import ProtectedEntitiesTVStations
from protected_entities_plmrs import ProtectedEntitiesPLMRS
import helpers

class Ruleset(object):
    """Ruleset"""

    def __init__(self, simulation):
        self.log = getModuleLogger(self)
        self._simulation = simulation

        self.set_propagation_model()

    @abstractmethod
    def name(self):
        """
        :rtype: string
        :return: the name of the ruleset
        """
        return

    @abstractmethod
    def location_is_whitespace(self, region, location, channel, device=None):
        """
        DOCUMENT ME

        :param region:
        :param location:
        :param device:
        :return:
        """
        return

    @abstractmethod
    def entity_is_protected(self, entity, location, channel=None):
        """Returns True if the entity is protected at that location (e.g. a point
        inside the coverage area of a TV station) and False otherwise.

        :param entity: instance of a subclass of :meth:`protected_entity.ProtectedEntity`
        :param location: (latitude, longitude)
        :type location: tuple
        :param channel: channel number of operation
        :type channel: integer
        :rtype: boolean
        :return: True if the entity is protected; False otherwise.
        """
        return

    @abstractmethod
    def entities_are_protected(self, entities, location, channel=None):
        """Returns True if one or more of the protected entities is protected at this location.

        :param entities: instance of a subclass of :meth:`protected_entities.ProtectedEntities`
        :param location: (latitude, longitude)
        :type location: tuple
        :param channel: channel number of operation
        :type channel: integer
        :rtype: boolean
        :return: True if the entity is protected; False otherwise.
        """

    @abstractmethod
    def classes_of_protected_entities(self):
        """
        :rtype: list of classes derived from :class:`protected_entity.ProtectedEntity`
        :return: entities which are protected in this ruleset (e.g. :class:`ProtectedEntityTVStation`)
        """

        """Returns a list of the entities which are protected in this ruleset (e.g. ProtectedEntityTVStation)."""
        return

    @abstractmethod
    def get_default_propagation_model(self):
        """
        :rtype: instance of :class:`propagation_model.PropagationModel`
        :return: the default propagation model for this ruleset (specified by the regulator)
        """
        return

    def set_propagation_model(self, propagation_model=None):
        """Sets the propagation model to be used with this ruleset. When called without arguments, the
         default propagation model is used.

        :param propagation_model: the propagation model to use with this ruleset
        :type propagation_model: :class:`propagation_model.PropagationModel` or None
        :return: None
        """
        self._propagation_model = propagation_model or self.get_default_propagation_model()

    def call_propagation_model(self, *args, **kwargs):
        """
        TODO: DOCUMENT ME

        :param args:
        :param kwargs:
        :return:
        """
        return self._propagation_model(*args, **kwargs)


class RulesetFcc2012(Ruleset):
    """Ruleset for FCC 2012 rules."""

    # @doc_inherit
    def name(self):
        return "FCC 2012 regulations"

    # @doc_inherit
    def entity_is_protected(self, entity, location, channel=None, device=None):
        # TODO: write this function

        # Only protect those specified by this ruleset
        if entity.__class__ not in self.classes_of_protected_entities():
            return False

        if isinstance(entity, ProtectedEntityTVStation):
            return self._tv_station_is_protected(entity, location, channel)
        else:
            self.log.error("Should not have reached this line")

        return True


    def _tv_station_is_protected(self, tv_station, location, channel, device=None):
        # TODO: update this

        # if not helpers.location_in_bounding_box(location, tv_station.get_bounding_box()):
        #     # self.log.debug("Not in bb")
        #     print tv_station.get_bounding_box()
        #     return False
        #
        # print("considering station")

        # tv_channel = tv_station.get_channel()
        # affected_channels = [tv_channel]
        # for chan in [tv_channel-1, tv_channel+1]:
        #     if helpers.channels_are_adjacent_in_frequency(self._simulation.get_mutable_region(), tv_channel, chan):
        #         affected_channels.append(chan)
        #
        # if channel not in affected_channels:
        #     return False

        erp_watts = tv_station.get_erp_watts()
        haat_meters = tv_station.get_haat_meters()
        tv_location = tv_station.get_location()

        distance = helpers.latlong_to_km(tv_location, location)
        frequency = self._simulation.get_mutable_region().get_center_frequency(channel)
        tx_height = haat_meters
        #if self._propagation_model.requires_rx_height():
        rx_height = device.get_haat()

        if distance < 100:
            return True
        else:
            return False

        # if self._propagation_model.requires_terrain():
        #     self.log.error("Terrain-based propagation models are not yet supported")
        #     return None
        # else:
        #     pathloss = self._propagation_model.get_pathloss_coefficient(distance, frequency, tx_height, rx_height)
        #
        # # print("PL = ", pathloss)
        # # print("rx power = ", erp_watts * pathloss)
        #
        # if erp_watts * pathloss > 200:
        #     self.log.error("BIG pathloss!")
        #     return True
        # else:
        #     return False



    def _cochannel_tv_station_is_protected(self, tv_station, location, channel, device=None):
        tv_location = tv_station.get_location()
        distance = helpers.latlong_to_km(tv_location, location)

        if distance < 100:
            return True
        else:
            return False

        # erp_watts = tv_station.get_erp_watts()
        # haat_meters = tv_station.get_haat_meters()
        # frequency = self._simulation.get_mutable_region().get_center_frequency(channel)
        # tx_height = haat_meters
        # #if self._propagation_model.requires_rx_height():
        # rx_height = device.get_haat()

    def _adjacent_channel_tv_station_is_protected(self, tv_station, location, channel, device=None):
        tv_location = tv_station.get_location()
        distance = helpers.latlong_to_km(tv_location, location)

        if distance < 80:
            return True
        else:
            return False

        # erp_watts = tv_station.get_erp_watts()
        # haat_meters = tv_station.get_haat_meters()
        # frequency = self._simulation.get_mutable_region().get_center_frequency(channel)
        # tx_height = haat_meters
        # #if self._propagation_model.requires_rx_height():
        # rx_height = device.get_haat()


    def _plmrs_is_protected(self, plmrs_entry, location, channel):
        plmrs_channel = plmrs_entry.get_channel()
        # affected_channels = [plmrs_channel]
        # for chan in [plmrs_channel-1, plmrs_channel+1]:
        #     if helpers.channels_are_adjacent_in_frequency(self._simulation.get_mutable_region(), plmrs_channel, chan):
        #         affected_channels.append(chan)
        #
        # if channel not in affected_channels:
        #     return False

        distance = helpers.latlong_to_km(plmrs_entry.get_location(), location)
        if plmrs_entry.is_metro():
            if distance > 134:
                return False
            elif distance > 131 and channel != plmrs_channel:   # adjacent-channel restrictions
                return False
            else:
                return True
        else:
            if distance > 54:
                return False
            elif distance > 51 and channel != plmrs_channel:   # adjacent-channel restrictions
                return False
            else:
                return True



    # @doc_inherit
    def classes_of_protected_entities(self):
        # TODO: add more entities to FCC ruleset
        return [ProtectedEntityTVStation, ]


    # @doc_inherit
    def get_default_propagation_model(self):
        return PropagationModelFreeSpace()  # TODO: update to f-curves



    def _location_is_whitespace_tv_stations_only(self, region, location, channel, device=None):
        # affected_channels = helpers.get_cochannel_and_first_adjacent(region, channel)
        #
        # tv_stations_container = region.get_protected_entities_of_type(ProtectedEntitiesTVStations)
        # for tv_station in tv_stations_container.list_of_entities():
        #     if not tv_station.get_channel() in affected_channels:
        #         continue
        #     if self._tv_station_is_protected(tv_station, location, channel, device):
        #         return False
        # return True

        tv_stations_container = region.get_protected_entities_of_type(ProtectedEntitiesTVStations)
        cochannel_stations = tv_stations_container.get_list_of_entities_on_channel(channel)

        for station in cochannel_stations:
            if self._cochannel_tv_station_is_protected(station, location, channel, device):
                return False

        adjacent_channel_stations = []
        for adj_chan in [channel-1, channel+1]:
            if helpers.channels_are_adjacent_in_frequency(region, adj_chan, channel):
                adjacent_channel_stations += tv_stations_container.get_list_of_entities_on_channel(adj_chan)

        for station in adjacent_channel_stations:
            if self._adjacent_channel_tv_station_is_protected(station, location, channel, device):
                return False

        return True


    def _location_is_whitespace_plmrs_only(self, region, location, channel, device=None):
        affected_channels = helpers.get_cochannel_and_first_adjacent(region, channel)

        plmrs_container = region.get_protected_entities_of_type(ProtectedEntitiesPLMRS)
        for plmrs_entry in plmrs_container.list_of_entities():
            if not plmrs_entry.get_channel() in affected_channels:
                continue
            if self._plmrs_is_protected(plmrs_entry, location, channel):
                return False
        return True


    # @doc_inherit
    def location_is_whitespace(self, region, location, channel, device=None):
        #protected_entities = region.protected_entities()

        if not self._location_is_whitespace_tv_stations_only(region, location, channel, device):
            return False

        # if not self._location_is_whitespace_plmrs_only(region, location, channel, device):
        #     return False

        # TODO: think about how to add wireless microphone protections (the 2 extra channels)

        return True

    def turn_grid_into_whitespace_map(region, is_whitespace_grid, channel, device):

        # Initialize to True
        is_whitespace_grid.reset_all_values(True)

        # tv_stations_container = region.get_protected_entities_of_type(ProtectedEntitiesTVStations)
        # cochannel_stations = tv_stations_container.get_list_of_entities_on_channel(channel)
        #
        # for adj_chan in [channel-1, channel+1]:
        #

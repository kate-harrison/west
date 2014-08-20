
from abc import ABCMeta
from device import Device
from os import path


# from protected_entities_us import ProtectedEntitiesUS
# from configuration_us import ConfigurationUS
# from pathloss_model_freespace import PathlossModelFreeSpace



class Simulation(object):
    """Generic simulation"""
    __metaclass__ = ABCMeta


    def __init__(self, ruleset_class, region_class, device):
        self._ruleset = ruleset_class(self)
        self._region = region_class(self)
        self._device = device


    def base_data_directory(self):
        """
        :return: string representing the path to the data directory
        :rtype: string
        """
        return path.join("data")

    def set_propagation_model(self, propagation_model):
        """Sets the propagation model to be used with this simulation. When called without arguments, the
         default propagation model is used.

        :param propagation_model: the propagation model to use with this ruleset
        :type propagation_model: :class:`propagation_model.PropagationModel` or None
        :return: None
        """
        self._ruleset.set_propagation_model(propagation_model)

    def set_allowed_channels(self, allowed_channels):
        # TODO: write this function
        pass

    def disable_protected_entity_type(self, type):
        # TODO: write this function
        # Will take string or class name input?
        pass

    def disable_terrain(self):
        # TODO: write this function
        # enable_terrain() ?
        pass

    def get_mutable_ruleset(self):
        """
        :rtype: :class:`ruleset.Ruleset`
        :return: the ruleset used for this simulation
        """
        return self._ruleset

    def get_mutable_region(self):
        """
        :rtype: :class:`region.Region`
        :return: the region used for this simulation
        """
        return self._region

    def get_mutable_device(self):
        """
        :return: the default device used for this simulation
        :rtype: :class:`device.Device` object
        """

    def set_device(self, device):
        """
        :param device: device to use for the simulation
        :type device: :class:`device.Device`
        :return: None
        """
        if device is None:
            raise TypeError("Expected an object of type Device")
        if not isinstance(device, Device):
            raise TypeError("Expected an object of type Device")
        self._device = device


    def location_is_whitespace(self, location, channel, device=None):
        device = device or self._device
        # TODO: FINISH
        #print("This is not finished yet")
        #
        # if not self._region.location_is_in_region(location):
        #     return False

        if channel not in self._region.get_tvws_channel_list():
            return False

        if device.is_portable() and (channel not in self._region.get_portable_tvws_channel_list()):
            return False

        return self._ruleset.location_is_whitespace(self._region, location, channel, device)

        
    def turn_data_map_into_whitespace_map(self, is_whitespace_grid, channel, device=None):
        device = device or self._device

        return self._ruleset.turn_data_map_into_whitespace_map(self._region, is_whitespace_grid, channel, device)


    # def __init__(self, config_class, propagation_model_class, protected_entities_class):
    #     self.configuration = config_class(self)
    #     self.propagation_model = propagation_model_class()
    #     self.protected_entities = protected_entities_class(self)




# class SimulationUS(Simulation):
#     """US-specific simulation"""
#     def __init__(self, device):
#         self.configuration = ConfigurationUS(self)
#         self.pathloss_model = PathlossModelFreeSpace()
#         self.protected_entities = ProtectedEntitiesUS(self)
#         self.device = device

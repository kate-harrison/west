from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger


class Ruleset(object):
    """Ruleset"""
    __metaclass__ = ABCMeta

    def __init__(self):
        self.log = getModuleLogger(self)

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
        Determines whether a location is considered whitespace, taking all
        relevant protections into account.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param location: (latitude, longitude)
        :type location: tuple of floats
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :return: True if the location is whitespace; False otherwise
        :rtype: bool
        """
        return

    @abstractmethod
    def classes_of_protected_entities(self):
        """
        Returns a list of the entities which are protected in this ruleset
        (e.g. ProtectedEntityTVStation).

        :rtype: list of classes derived from \
            :class:`protected_entity.ProtectedEntity`
        :return: entities which are protected in this ruleset (e.g. \
            :class:`ProtectedEntityTVStation`)
        """
        return

    @abstractmethod
    def get_default_propagation_model(self):
        """
        :rtype: instance of :class:`propagation_model.PropagationModel`
        :return: the default propagation model for this ruleset (specified by \
            the regulator)
        """
        return

    def set_propagation_model(self, propagation_model=None):
        """Sets the propagation model to be used with this ruleset. When
        called without arguments, the default propagation model is used.

        :param propagation_model: the propagation model to use with this ruleset
        :type propagation_model: :class:`propagation_model.PropagationModel` \
            or None
        :return: None
        """
        self._propagation_model = propagation_model or \
                                  self.get_default_propagation_model()

    def get_mutable_propagation_model(self):
        """
        :return: the propagation model used with this ruleset
        :rtype: :class:`propagation_model.PropagationModel` object
        """
        return self._propagation_model

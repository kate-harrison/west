from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger

class Ruleset(object):
    """Ruleset"""

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

    def get_mutable_propagation_model(self):
        """
        :return: the propagation model used with this ruleset
        :rtype: :class:`propagation_model.PropagationModel` object
        """
        return self._propagation_model

from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger
# from doc_inherit import doc_inherit
import simplekml

class ProtectedEntities(object):
    """Protected entities: a collection of protected entities."""
    __metaclass__ = ABCMeta

    def __init__(self, simulation):
        self.simulation = simulation
        self.log = getModuleLogger(self)

        self._reset_entities()

        self.log.debug("Loading protected entities")
        #try:
        self._load_entities()
        #except Exception as e:
        #    self.log.error("Unknown error loading one or more protected entities")

    @abstractmethod
    def _load_entities(self):
        """Load the protected entities."""
        return

    @abstractmethod
    def source_filename(self):
        """Filename for the source data."""
        return

    @abstractmethod
    def source_name(self):
        """String version of the source data."""
        return

    def list_of_entities(self):
        """List of entities."""
        return self._entities

    def _reset_entities(self):
        """Reset the set of protected entities."""
        # self.log.debug("Resetting the set of protected entities.")
        self._entities = []

    def _add_entity(self, new_entity):
        """Add a new protected entity."""
        self._entities.append(new_entity)

    def get_list_of_entities_on_channel(self, channel):
        """
        Returns an empty list if channel is not an attribute of this type of ProtectedEntity.

        :param channel:
        :return:
        """
        return [entity for entity in self.list_of_entities() if entity.get_channel() == channel]


    def export_to_kml(self, kml_filename, save=True, filter_fcn=None):
            """
            Exports the ProtectedEntities as a KML file.

            :param save: if True, saves the file using the filename provided by :meth:`kml_filename`.
            :type save: boolean
            :return:
            :rtype: KML object (e.g. output from :meth:`simplekml.Kml`)
            """

            list_of_entities = self.list_of_entities()
            if filter_fcn is not None:
                list_of_entities = [entity for entity in list_of_entities if filter_fcn(entity)]

            kml = simplekml.Kml()
            for entity in list_of_entities:
                entity.add_to_kml(kml)

            if save:
                kml.save(kml_filename)

            return kml


class ProtectedEntitiesDummy(ProtectedEntities):
    """Dummy protected entities (passthrough)."""

    # @doc_inherit
    def _load_entities(self):
        pass

    # @doc_inherit
    def source_filename(self):
        return None

    # @doc_inherit
    def source_name(self):
        return "None"

    # @doc_inherit
    def list_of_entities(self):
        return []

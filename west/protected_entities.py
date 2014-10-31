from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger
import simplekml


class ProtectedEntities(object):
    """Protected entities: a collection of protected entities."""
    __metaclass__ = ABCMeta

    def __init__(self, region):
        self.log = getModuleLogger(self)

        self.region = region

        self._reset_entities()

        self.log.debug("Loading protected entities")
        self._load_entities()

        self._refresh_cached_data()

    @abstractmethod
    def _load_entities(self):
        """Load the protected entities."""
        return

    def get_mutable_region(self):
        """
        :return: the region corresponding to this set of protected entities
        :rtype: :class:`region.Region` object
        """
        return self.region

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
        self._entities = []

    def _add_entity(self, new_entity):
        """
        Add a new protected entity. Does NOT update any internal caches. The
        caller is expected to call :meth:`_refresh_cached_data` after adding
        all entities.

        :param new_entity: the entity to be added
        :type new_entity: :class:`protected_entity.ProtectedEntity`
        """
        self._entities.append(new_entity)

    def add_entity(self, new_entity, update_internal_data_caches=True):
        """
        Add a new protected entity. By default, this function updates
        internal data caches. If adding many entities in succession, consider
        updating the caches only when adding the last entity.

        :param new_entity: the entity to be added
        :type new_entity: :class:`protected_entity.ProtectedEntity`
        :param update_internal_data_caches: if True, updates internal data \
                caches via :meth:`_refresh_cached_data`.
        :type update_internal_data_caches: bool
        """
        self._add_entity(new_entity)
        if update_internal_data_caches:
            self._refresh_cached_data()

    def get_list_of_entities_on_channel(self, channel_number):
        """
        Returns an empty list if channel is not an attribute of this type of
        ProtectedEntity. Raises a ValueError if the channel number is
        unsupported by the :class:`region.Region`.

        :param channel:
        :return:
        """
        if channel_number not in self.region.get_channel_list():
            raise ValueError("Unsupported channel number: %d" % channel_number)
        return [entity for entity in self.list_of_entities() if
                entity.get_channel() == channel_number]

    def remove_entities(self, filter_function):
        """
        Removes entities for which ``filter_function(entity)`` does *not*
        return True or a "truthy" value.

        :param filter_function: handle to a function which returns True for \
                entities which should be kept and False otherwise; takes a \
                single argument of type :class:`ProtectedEntity`.
        :return: None
        """
        old_entities = self._entities
        self._reset_entities()
        for entity in old_entities:
            if filter_function(entity):
                self._add_entity(entity)

        self._refresh_cached_data()


    def _refresh_cached_data(self):
        """
        Use this function to create/refresh any data that might be cached in
        the ProtectedEntities object.
        """
        pass


    def export_to_kml(self, kml_filename, filter_function=None,
                      group_by_channel=True, save=True):
        """
        Exports the ProtectedEntities as a KML file. If ``filter_function``
        is provided, includes only entities for which
        ``filter_function(entity)`` returns True or a "truthy" value.

        :param filter_function: handle to a function which returns True for \
                entities which should be kept and False otherwise; takes a \
                single argument of type :class:`ProtectedEntity`.
        :param group_by_channel: if True, groups entities into folders by \
                channel number
        :type group_by_channel: boolean
        :param save: if True, saves the file using the filename provided by \
                :meth:`kml_filename`.
        :type save: boolean
        :return:
        :rtype: KML object (e.g. output from :meth:`simplekml.Kml`)
        """

        list_of_entities = self.list_of_entities()
        if filter_function is not None:
            list_of_entities = [entity for entity in list_of_entities if
                                filter_function(entity)]

        kml = simplekml.Kml()

        if group_by_channel:
            folders = {}
            for channel in self.region.get_channel_list():
                folders[channel] = kml.newfolder(name="Channel %d" % channel)

        for entity in list_of_entities:
            if group_by_channel:
                channel = entity.get_channel()
                entity.add_to_kml(folders[channel])
            else:
                entity.add_to_kml(kml)

        if save:
            kml.save(kml_filename)

        return kml

    @abstractmethod
    def get_max_protected_radius_km(self):
        """
        This method returns the maximum protected radius that could be apply
        to any entity in this collection. This value is used for creating a
        bounding box which later speeds up computations.

        .. warning:: Set to a larger value than expected to be needed for any \
            ruleset! Otherwise entries may be erroneously skipped.
        """
        return


class ProtectedEntitiesDummy(ProtectedEntities):
    """Dummy protected entities (passthrough)."""

    def _load_entities(self):
        pass

    def source_filename(self):
        return None

    def source_name(self):
        return "None"

    def list_of_entities(self):
        return []

    def get_max_protected_radius_km(self):
        return 0

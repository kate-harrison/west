import os
import csv
from protected_entity_plmrs import ProtectedEntityPLMRS
from protected_entities import ProtectedEntities
import configuration

class ProtectedEntitiesPLMRS(ProtectedEntities):
    """
    Intermediate class
    """


class ProtectedEntitiesPLMRSUnitedStatesFromGoogle(ProtectedEntitiesPLMRS):
    """
    PLMRS exclusions with data from Google
    """

    def source_filename(self):
        base_directory = configuration.paths['UnitedStates']['protected_entities']
        return os.path.join(base_directory, 'FromGoogle', 'plcmrs.csv')

    def source_name(self):
        return "Google TVWS database download [" \
               "http://www.google.com/get/spectrumdatabase/data/]"

    def get_max_protected_radius_km(self):
        """
        See :meth:`protected_entities.ProtectedEntities.get_max_protected_radius_km` for more details.

        :return: 150.0
        :rtype: float
        """
        return 150.0

    # {'rcamsl_meters': '51.8', 'application_id': '2641127', 'uid': 'WQAS562', 'erp_watts': '250000.000',
    # 'site_number': '2', 'parent_latitude': '', 'entity_type': 'PLCMRS', 'keyhole_radius_meters': '',
    # 'antenna_rotation_degrees': '0.0', 'latitude': '38.956611', 'tx_type': 'PW', 'channel': '18', 'parent_longitude': '',
    # 'facility_id': '0', 'circle_radius_meters': '', 'location_type': 'POINT', 'data_source': 'ULS', 'rcagl_meters': '0.0',
    # 'geometry': '', 'longitude': '-78.023528', 'haat_meters': '0.0', 'azimuth': '', 'antenna_id': '0',
    # 'parent_facility_id': '', 'parent_callsign': ''}


    # @doc_inherit
    def _load_entities(self):
        self.log.debug("Loading PLMRS data from \"%s\" (%s)" % (str(self.source_filename()), str(self.source_name())))

        with open(self.source_filename(), 'r') as f:
            plmrs_csv = csv.DictReader(f)
            for plmrs_entry in plmrs_csv:
                #print(plmrs_entry)
                latitude = float(plmrs_entry["latitude"])
                longitude = float(plmrs_entry["longitude"])
                channel = int(plmrs_entry["channel"])

                tx_type = plmrs_entry["tx_type"]
                is_metro = (tx_type == "TX_TYPE_UNKNOWN")

                description = plmrs_entry['uid']

                new_plmrs_entry = ProtectedEntityPLMRS(self, self.get_mutable_region(), latitude, longitude, channel,
                                                       is_metro, description)
                self._add_entity(new_plmrs_entry)

    def _refresh_cached_data(self):
        self.log.debug("Categorizing entities by channel")
        self.entities_by_channel = {}

        # Pre-allocate the channels so that an empty list is returned even if there
        # are no stations on that channel. Stations which have a channel not in the
        # list will not be added.
        for channel_number in self.region.get_channel_list():
            self.entities_by_channel[channel_number] = []

        for entity in self.list_of_entities():
            channel = entity.get_channel()

            if channel not in self.entities_by_channel:
                self.log.warning("Detected a PLMRS entity on an unsupported channel: %d" % channel)
            else:
                self.entities_by_channel[channel].append(entity)

    def get_list_of_entities_on_channel(self, channel_number):
        if channel_number not in self.region.get_channel_list():
            raise ValueError("Unsupported channel number: %d" % channel_number)
        return self.entities_by_channel[channel_number]

import os
import csv
from protected_entity_plmrs import ProtectedEntityPLMRS
from protected_entities import ProtectedEntities

class ProtectedEntitiesPLMRS(ProtectedEntities):
    """
    Intermediate class
    """



class ProtectedEntitiesPLMRSUnitedStatesFromGoogle(ProtectedEntitiesPLMRS):
    """
    PLMRS exclusions with data from Google
    """

    def source_filename(self):
        return os.path.join("data", "Google data", "plcmrs.csv")

    def source_name(self):
        return "Google TVWS database download [" \
               "http://www.google.com/get/spectrumdatabase/data/]"

    def get_max_protected_radius_km(self):
        return 150

    # {'rcamsl_meters': '51.8', 'application_id': '2641127', 'uid': 'WQAS562', 'erp_watts': '250000.000',
    # 'site_number': '2', 'parent_latitude': '', 'entity_type': 'PLCMRS', 'keyhole_radius_meters': '',
    # 'antenna_rotation_degrees': '0.0', 'latitude': '38.956611', 'tx_type': 'PW', 'channel': '18', 'parent_longitude': '',
    # 'facility_id': '0', 'circle_radius_meters': '', 'location_type': 'POINT', 'data_source': 'ULS', 'rcagl_meters': '0.0',
    # 'geometry': '', 'longitude': '-78.023528', 'haat_meters': '0.0', 'azimuth': '', 'antenna_id': '0',
    # 'parent_facility_id': '', 'parent_callsign': ''}


    # @doc_inherit
    def _load_entities(self):
        self.log.debug("Loading PLMRS data from %s (%s)" % (str(self.source_filename()), str(self.source_name())))

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

from protected_entities import ProtectedEntities
from protected_entity_radio_astronomy_site import ProtectedEntityRadioAstronomySite
import os
import csv

class ProtectedEntitiesRadioAstronomySites(ProtectedEntities):
    """
    Intermediate class
    """


class ProtectedEntitiesRadioAstronomySitesUnitedStates(ProtectedEntitiesRadioAstronomySites):
    def source_filename(self):
        return os.path.join("data", "Radioastronomy sites (FCC regulations 2012) - Sheet1.csv")

    def source_name(self):
        return "FCC 2012 regulations: section 15.712(h)(3)"

    def get_max_protected_radius_km(self):
        return 10

    def _load_entities(self):
        """Load the protected entities."""

        self.log.debug("Loading radio astronomy sites from %s (%s)" % (str(self.source_filename()), str(self.source_name())))

        def str2bool(v):
            return v.lower() in ("yes", "true", "t", "1")

        ras_channel = 37

        with open(self.source_filename(), 'r') as f:
            ras_csv = csv.DictReader(f)
            for ras_entry in ras_csv:
                # print ras_entry

                try:
                    lat_deg = float(ras_entry['Latitude (degree)'])
                    lat_min = float(ras_entry['Latitude (minute)'])
                    lat_sec = float(ras_entry['Latitude (second)'])
                    lat_dir = ras_entry['Latitude (direction)']
                    if lat_dir.lower() in ["n", "north"]:
                        lat_mult = 1.0
                    else:
                        lat_mult = -1.0
                    latitude = lat_mult * (lat_deg + lat_min/60 + lat_sec/3600)

                    lon_deg = float(ras_entry['Longitude (degree)'])
                    lon_min = float(ras_entry['Longitude (minute)'])
                    lon_sec = float(ras_entry['Longitude (second)'])
                    lon_dir = ras_entry['Longitude (direction)']
                    if lon_dir.lower() in ["e", "east"]:
                        lon_mult = 1.0
                    else:
                        lon_mult = -1.0
                    longitude = lon_mult * (lon_deg + lon_min/60 + lon_sec/3600)

                    name = ras_entry['Name']

                    is_point = str2bool(ras_entry['Is point'])

                    if is_point:
                        latitude_deviation = None
                        longitude_deviation = None
                    else:
                        latitude_deviation = float(ras_entry['Latitude deviation (decimal degrees)'])
                        longitude_deviation = float(ras_entry['Longitude deviation (decimal degrees)'])

                    new_ras_entry = ProtectedEntityRadioAstronomySite(container=self,
                                                                      region=self.get_mutable_region(),
                                                                      latitude=latitude,
                                                                      longitude=longitude,
                                                                      channel=ras_channel,
                                                                      name=name,
                                                                      is_point=is_point,
                                                                      latitude_deviation=latitude_deviation,
                                                                      longitude_deviation=longitude_deviation)

                    self._add_entity(new_ras_entry)

                except Exception as e:
                    self.log.error("Error reading in radio astronomy sites: " + str(e) + " (last site read: " + str(name) + ")")

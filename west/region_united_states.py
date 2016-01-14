from region import Region
import boundary
import protected_entities_tv_stations
import protected_entities_plmrs
import protected_entities_radio_astronomy_sites
from protected_entities import ProtectedEntitiesDummy

class RegionUnitedStates(Region):
    """United States region"""

    # If the device's height is not specified, this height will be used.
    default_device_haat_meters = 10

    def _get_boundary_class(self):
        return boundary.BoundaryContinentalUnitedStates

    def _load_protected_entities(self):
        self.protected_entities[
            protected_entities_tv_stations.ProtectedEntitiesTVStations] = \
            protected_entities_tv_stations\
                .ProtectedEntitiesTVStationsUnitedStatesTVQuery2014June17(self)

        self.protected_entities[
            protected_entities_plmrs.ProtectedEntitiesPLMRS] = \
            protected_entities_plmrs\
                .ProtectedEntitiesPLMRSUnitedStatesFromGoogle(self)

        self.protected_entities[
            protected_entities_radio_astronomy_sites
                .ProtectedEntitiesRadioAstronomySites] = \
            protected_entities_radio_astronomy_sites\
                .ProtectedEntitiesRadioAstronomySitesUnitedStates(self)

    def get_frequency_bounds(self, channel):
        if channel in [2, 3, 4]:
            low = (channel - 2) * 6 + 54
            high = (channel - 2) * 6 + 60
        elif channel in [5, 6]:
            low = (channel - 5) * 6 + 76
            high = (channel - 5) * 6 + 82
        elif 7 <= channel <= 13:
            low = (channel - 7) * 6 + 174
            high = (channel - 7) * 6 + 180
        elif 14 <= channel <= 69:
            low = (channel - 14) * 6 + 470
            high = (channel - 14) * 6 + 476
        else:
            raise ValueError("Invalid channel number: %d" % channel)
        return low, high

    def get_tvws_channel_list(self):
        # 2, 5-36, 38-51
        return [2] + range(5, 37) + range(38, 52)

    def get_portable_tvws_channel_list(self):
        # 21-36, 38-51
        return range(21, 37) + range(38, 52)

    def get_channel_list(self):
        # 2-51
        return range(2, 52)

    def get_channel_width(self):
        return 6e6


class RegionUnitedStatesTvOnly(RegionUnitedStates):
    """A descendant of :class:`RegionUnitedStates` which has only TV stations as
    its protected entities."""

    def _load_protected_entities(self):
        self.protected_entities[
            protected_entities_tv_stations.ProtectedEntitiesTVStations] = \
            protected_entities_tv_stations \
                .ProtectedEntitiesTVStationsUnitedStatesTVQuery2014June17(self)

        self.protected_entities[
            protected_entities_plmrs.ProtectedEntitiesPLMRS] = \
            ProtectedEntitiesDummy(self)

        self.protected_entities[
            protected_entities_radio_astronomy_sites
                .ProtectedEntitiesRadioAstronomySites] = \
            ProtectedEntitiesDummy(self)

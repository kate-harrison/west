from region import Region
# from doc_inherit import doc_inherit
#from boundary import BoundaryContinentalUnitedStates
import boundary
import protected_entities_tv_stations
import protected_entities
import protected_entities_plmrs

class RegionUnitedStates(Region):
    """US region"""

    # def __init__(self, *args, **kwargs):
    #     super(RegionUnitedStates, self).__init__(*args, **kwargs)
    #     self._load_population()
    #     self._load_terrain()
    #     self._load_boundary()
    #     self._load_economic_data()


    # If the device's height is not specified, this height will be used.
    default_device_haat_meters = 10

    # @doc_inherit
    def _get_boundary_class(self):
        return boundary.BoundaryContinentalUnitedStates

    # @doc_inherit
    def _load_protected_entities(self):
        self.protected_entities[protected_entities_tv_stations.ProtectedEntitiesTVStations] = \
            protected_entities_tv_stations.ProtectedEntitiesTVStationsUnitedStatesFromGoogle(self.simulation)

        self.protected_entities[protected_entities_plmrs.ProtectedEntitiesPLMRS] = \
            protected_entities_plmrs.ProtectedEntitiesPLMRSUnitedStatesFromGoogle(self.simulation)


    # @doc_inherit
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
            low = None
            high = None
            #print("ERROR: incorrect channel number:", channel)
        if low is not None:
            low *= 1e6
            high *= 1e6
        return (low, high)

    # @doc_inherit
    def get_tvws_channel_list(self):
        # 2-36, 38-51
        return range(2, 37) + range(38, 52)

    # @doc_inherit
    def get_portable_tvws_channel_list(self):
        # 21-51
        return range(21, 52)

    # @doc_inherit
    def get_channel_list(self):
        # 2-51
        return range(2, 52)

    # @doc_inherit
    def get_channel_width(self):
        return 6e6


from protected_entity_tv_station import ProtectedEntityTVStation
from protected_entities_tv_stations import ProtectedEntitiesTVStations
from protected_entities_plmrs import ProtectedEntitiesPLMRS
from protected_entities_radio_astronomy_sites import ProtectedEntitiesRadioAstronomySites
from propagation_model_fcurves import PropagationModelFcurves
import helpers
from geopy.distance import vincenty
from propagation_model import PropagationCurve
from ruleset import Ruleset


class RulesetFcc2012(Ruleset):
    """Ruleset for FCC 2012 rules."""

    _low_vhf_lower_frequency_mhz = 54   # US channel 2 (lower edge)
    _low_vhf_upper_frequency_mhz = 88   # US channel 6 (upper edge)

    _high_vhf_lower_frequency_mhz = 174  # US channel 7 (lower edge)
    _high_vhf_upper_frequency_mhz = 216  # US channel 13 (upper edge)

    _uhf_lower_frequency_mhz = 470      # US channel 14 (lower edge)
    _uhf_upper_frequency_mhz = 890      # US channel 83 (upper edge)

    def name(self):
        return "FCC 2012 regulations"

    def classes_of_protected_entities(self):
        # TODO: add more entities to FCC ruleset
        return [ProtectedEntityTVStation, ]

    def get_default_propagation_model(self):
        return PropagationModelFcurves()

    def entity_is_protected(self, entity, location, channel=None, device=None):
        # TODO: write this function

        # Only protect those specified by this ruleset
        if entity.__class__ not in self.classes_of_protected_entities():
            return False

        if isinstance(entity, ProtectedEntityTVStation):
            return self._tv_station_is_protected(entity, location, channel)
        else:
            self.log.error("Should not have reached this line")

        return True

####
#   TV STATION PROTECTION CALCULATIONS
#   (separate section for protection tables)
####
    def _tv_station_is_protected(self, tv_station, location, channel, device=None):
        # TODO: update this
        pass

    def get_tv_protected_radius_km(self, tv_station, device_location):
        """
        Determines the protected radius of the TV station in the direction of `device_location`.

        :param tv_station: the TV station of interest
        :type tv_station: :class:`protected_entity_tv_station.ProtectedEntityTVStation`
        :param device_location: (latitude, longitude)
        :type device_location: tuple of floats
        :return: the protected radius of the TV station in kilometers
        :rtype: float
        """
        freq = tv_station.get_center_frequency()

        curve = self.get_tv_curve(tv_station.is_digital())
        target_field_strength_dBu = self.get_tv_target_field_strength_dBu(tv_station.is_digital(), freq)

        tv_location = tv_station.get_location()

        desired_Watts = self._propagation_model.dBu_to_Watts(target_field_strength_dBu, freq)
        tv_power_Watts = tv_station.get_erp_watts()
        pathloss_coefficient = desired_Watts / tv_power_Watts
        protection_distance_km = self._propagation_model.get_distance(pathloss_coefficient,
                                                                      frequency=freq,
                                                                      tx_height=tv_station.get_haat_meters(),
                                                                      tx_location=tv_location,
                                                                      rx_location=device_location,
                                                                      curve_enum=curve)
        return protection_distance_km

    def cochannel_tv_station_is_protected(self, tv_station, device_location, device_haat):
        """
        Determines whether or not the TV station is protected on a cochannel basis.

        .. note:: The device's proposed channel is not checked.

        .. warning:: Uses the TV station's bounding box (whose dimensions are set in
         :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`) to speed up computations. If these
         dimensions are too small, TV stations will be erroneously excluded from this computation.

        :param tv_station:
        :type tv_station: :class:`protected_entity_tv_station.ProtectedEntityTVStation`
        :param device_location: (latitude, longitude)
        :type device_location: tuple of floats
        :param device_haat: the height above average terrain (HAAT) of the device in meters
        :type device_haat: float
        :return: True if the station is protected on a cochannel basis; False otherwise
        :rtype: bool
        """

        if not tv_station.location_in_bounding_box(device_location):
            return False

        actual_distance_km = vincenty(tv_station.get_location(), device_location).kilometers
        protection_distance_km = self.get_tv_protected_radius_km(tv_station, device_location)
        separation_distance_km = self.get_tv_cochannel_separation_distance_km(device_haat)

        # Check if we are inside the protected contour
        if actual_distance_km <= protection_distance_km + separation_distance_km:
            return True
        else:
            return False

    def adjacent_channel_tv_station_is_protected(self, tv_station, device_location, device_haat):
        """
        Determines whether or not the TV station is protected on an adjacent-channel basis.

        .. note:: The device's proposed channel is not checked.

        .. warning:: Uses the TV station's bounding box (whose dimensions are set in
         :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`) to speed up computations. If these
         dimensions are too small, TV stations will be erroneously excluded from this computation.

        :param tv_station:
        :type tv_station: :class:`protected_entity_tv_station.ProtectedEntityTVStation`
        :param device_location: (latitude, longitude)
        :type device_location: tuple of floats
        :param device_haat: the height above average terrain (HAAT) of the device in meters
        :type device_haat: float
        :return: True if the station is protected on an adjacent-channel basis; False otherwise
        :rtype: bool
        """

        if not tv_station.location_in_bounding_box(device_location):
            return False

        actual_distance_km = vincenty(tv_station.get_location(), device_location).kilometers
        protection_distance_km = self.get_tv_protected_radius_km(tv_station, device_location)
        separation_distance_km = self.get_tv_adjacent_channel_separation_distance_km(device_haat)

        # Check if we are inside the protected contour
        return actual_distance_km <= (protection_distance_km + separation_distance_km)

    def location_is_whitespace_tv_stations_only(self, region, location, device_channel, device_haat):
        """
        Determines whether a location is considered whitespace *on the basis of TV station protections alone.*

        .. note:: Does not check to see if the location is within the region.

        :param region: region containing the TV stations
        :type region: :class:`region.Region` object
        :param location: (latitude, longitude)
        :type location: tuple of floats
        :param device_channel: channel to be tested for whitespace
        :type device_channel: int
        :param device_haat: height above average terrain (HAAT) of the device, in meters
        :type device_haat: float
        :return: True if the location is whitespace; False otherwise
        :rtype: bool
        """
        tv_stations_container = region.get_protected_entities_of_type(ProtectedEntitiesTVStations)
        cochannel_stations = tv_stations_container.get_list_of_entities_on_channel(device_channel)

        for station in cochannel_stations:
            if self.cochannel_tv_station_is_protected(station, location, device_haat):
                return False

        adjacent_channel_stations = []
        for adj_chan in [device_channel-1, device_channel+1]:
            if helpers.channels_are_adjacent_in_frequency(region, adj_chan, device_channel):
                adjacent_channel_stations += tv_stations_container.get_list_of_entities_on_channel(adj_chan)

        for station in adjacent_channel_stations:
            if self.adjacent_channel_tv_station_is_protected(station, location, device_haat):
                return False

        return True
####
#   END TV STATION PROTECTION CALCULATIONS
####


####
#   PLMRS PROTECTION CALCULATIONS
####
    def get_plmrs_exclusion_radius_km(self, is_metro, is_cochannel):
        """
        The separation distance mandated by the FCC depends on whether the PLMRS exclusion is a metropolitan region vs.
         an individual registration. It also depends on whether the proposed operation is cochannel or adjacent-channel.
         The values are given in section 15.712(d) of the FCC's rules and the translation is implemented in this
         function.

         .. warning:: This function assumes that the proposed operation is either cochannel or adjacent-channel. It does
         not check channel assignments or proposals.

        :param is_metro:
        :param is_cochannel:
        :return:
        """
        if is_metro:
            if is_cochannel:
                return 134.0
            else:
                return 131.0
        else:
            if is_cochannel:
                return 54.0
            else:
                return 51.0

    def plmrs_is_protected(self, plmrs_entry, location, device_channel, region):
        """
        Determines if a particular PLMRS entity is protected at the given location and on the specified channel.

        .. warning:: Uses the PLMRS entity's bounding box (whose dimensions are set in
         :class:`protected_entities_plmrs.ProtectedEntitiesPLMRS`) to speed up computations. If these
         dimensions are too small, PLMRS entities will be erroneously excluded from this computation.


        :param plmrs_entry: the PLMRS entity to be protected
        :type plmrs_entry: :class:`protected_entity_plmrs.ProtectedEntityPLMRS` object
        :param location: (latitude, longitude)
        :type location: tuple of floats
        :param device_channel: channel to be tested for whitespace
        :type device_channel: int
        :param region: region containing the PLMRS entities
        :type region: :class:`region.Region` object
        :return: True if the PLMRS entity is protected; False otherwise
        :rtype: bool
        """
        plmrs_channel = plmrs_entry.get_channel()

        is_cochannel = (plmrs_channel == device_channel)

        # PLMRS is only protected on cochannel and first-adjacent
        # We know it's not protected if it's neither cochannel nor in a first-adjacent channel
        if not is_cochannel and not helpers.channels_are_adjacent_in_frequency(region, plmrs_channel,
                                                                               device_channel):
            return False

        if not plmrs_entry.location_in_bounding_box(location):
            return False

        actual_distance_km = vincenty(plmrs_entry.get_location(), location).kilometers
        exclusion_radius_km = self.get_plmrs_exclusion_radius_km(plmrs_entry.is_metro(), is_cochannel)
        return actual_distance_km <= exclusion_radius_km

    def location_is_whitespace_plmrs_only(self, region, location, device_channel):
        """
        Determines whether a location is considered whitespace *on the basis of PLMRS protections alone.*

        .. note:: Does not check to see if the location is within the region.

        :param region: region containing the PLMRS entities
        :type region: :class:`region.Region` object
        :param location: (latitude, longitude)
        :type location: tuple of floats
        :param device_channel: channel to be tested for whitespace
        :type device_channel: int
        :return: True if the location is whitespace; False otherwise
        :rtype: bool
        """
        plmrs_container = region.get_protected_entities_of_type(ProtectedEntitiesPLMRS)
        for plmrs_entry in plmrs_container.list_of_entities():
            if self.plmrs_is_protected(plmrs_entry, location, device_channel, region):
                return False
        return True
####
#   END PLMRS PROTECTION CALCULATIONS
####

####
#   RADIOASTRONOMY PROTECTION CALCULATIONS
####

    def get_radioastronomy_site_exclusion_radius_km(self):
        """
        The radioastronomy separation distance mandated by the FCC is defined in section 15.712(h) of the FCC TVWS
        regulations. We include it as a parameter here to allow for easy modification.

        :return: exclusion radius for radioastronomy sites in kilometers
        :rtype: float
        """
        return 2.4

    def radioastronomy_site_is_protected(self, ras_site, device_location):
        if not ras_site.location_in_bounding_box(device_location):
            return False

        if ras_site.is_point():
            actual_distance_km = vincenty(ras_site.get_location(), device_location).kilometers
            return actual_distance_km <= self.get_radioastronomy_site_exclusion_radius_km()
        else:
            return ras_site.location_in_protected_polygon(device_location)

    def location_is_whitespace_radioastronomy_only(self, region, location):
        ras_container = region.get_protected_entities_of_type(ProtectedEntitiesRadioAstronomySites)
        for ras_site in ras_container.list_of_entities():
            if self.radioastronomy_site_is_protected(ras_site, location):
                return False
        return True

####
#   END RADIOASTRONOMY PROTECTION CALCULATIONS
####

####
#   GENERAL WHITESPACE CALCULATIONS
####

    def location_is_whitespace(self, region, location, channel, device=None):
        """
        Determines whether a location is considered whitespace, taking all protections into account (*except* wireless
        microphones).

        .. warning:: Does not include wireless microphone protections.

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

        # TODO: think about how to add wireless microphone protections (the 2 extra channels)

        device = device or self._simulation.get_mutable_device()
        device_haat = device.get_haat()

        #protected_entities = region.protected_entities()

        if not self.location_is_whitespace_tv_stations_only(region, location, channel, device_haat):
            return False

        if not self.location_is_whitespace_plmrs_only(region, location, channel):
            return False

        return True

    def turn_data_map_into_whitespace_map(self, region, is_whitespace_grid, channel, device, reset_grid=False):
        """
        Turns the input grid into a map of whitespace availability. A value of `True` means that whitespace is available
        in that location, whereas a value of `False` means that that location is not considered whitespace for the
        supplied device.

        .. note:: Any entries which are already `False` will not be evaluated unless `reset_grid=True`.

        Recommended usage is to initialize is_whitespace_grid to an is_in_region grid to avoid computations on locations
        which are outside of the region. No in-region testing is done otherwise.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_grid: grid to be filled with the output
        :type is_whitespace_grid: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :param reset_grid: if True, the grid is reset to `True` (i.e. "evaluate all") before computations begin
        :type reset_grid: bool
        :return: None
        """

        if reset_grid:
            # Initialize to True so that all points will be evaluated
            is_whitespace_grid.reset_all_values(True)

        self.apply_radioastronomy_exclusions_to_map(region, is_whitespace_grid)
        self.apply_plmrs_exclusions_to_map(region, is_whitespace_grid, channel)
        self.apply_tv_exclusions_to_map(region, is_whitespace_grid, channel, device)

        return is_whitespace_grid

    def apply_tv_exclusions_to_map(self, region, is_whitespace_grid, channel, device):
        """
        Applies TV exclusions to the given map. Entries will be marked `True` if they are whitespace and `False`
        otherwise.

        .. note:: Any entries which are already `False` will not be evaluated.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_grid: grid to be filled with the output
        :type is_whitespace_grid: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :return: None
        """
        self.log.info("Applying TV exclusions")
        for (lat_idx, lat) in enumerate(is_whitespace_grid.latitudes):
            if lat_idx % 10 == 0:
                print "Latitude number: %d" % lat_idx
            for (lon_idx, lon) in enumerate(is_whitespace_grid.longitudes):
                # Skip if not whitespace
                if not is_whitespace_grid.mutable_matrix[lat_idx, lon_idx]:
                    continue

                is_whitespace_grid.mutable_matrix[lat_idx, lon_idx] = \
                    self.location_is_whitespace_tv_stations_only(region, (lat, lon), channel, device.get_haat())

    def apply_plmrs_exclusions_to_map(self, region, is_whitespace_grid, channel):
        """
        Applies PLMRS exclusions to the given map. Entries will be marked `True` if they are whitespace and `False`
        otherwise.

        .. note:: Any entries which are already `False` will not be evaluated.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_grid: grid to be filled with the output
        :type is_whitespace_grid: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :return: None
        """
        self.log.info("Applying PLMRS exclusions")
        for (lat_idx, lat) in enumerate(is_whitespace_grid.latitudes):
            if lat_idx % 10 == 0:
                print "Latitude number: %d" % lat_idx
            for (lon_idx, lon) in enumerate(is_whitespace_grid.longitudes):
                # Skip if not whitespace
                if not is_whitespace_grid.mutable_matrix[lat_idx, lon_idx]:
                    continue

                is_whitespace_grid.mutable_matrix[lat_idx, lon_idx] = \
                    self.location_is_whitespace_plmrs_only(region, (lat, lon), channel)

    def apply_radioastronomy_exclusions_to_map(self, region, is_whitespace_grid):
        """
        Applies radioastronomy exclusions to the given map. Entries will be marked `True` if they are whitespace and
        `False` otherwise.

        .. note:: Any entries which are already `False` will not be evaluated.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_grid: grid to be filled with the output
        :type is_whitespace_grid: :class:`data_map.DataMap2D` object
        :return: None
        """
        self.log.info("Applying radioastronomy exclusions")
        for (lat_idx, lat) in enumerate(is_whitespace_grid.latitudes):
            for (lon_idx, lon) in enumerate(is_whitespace_grid.longitudes):
                # Skip if not whitespace
                if not is_whitespace_grid.mutable_matrix[lat_idx, lon_idx]:
                    continue

                is_whitespace_grid.mutable_matrix[lat_idx, lon_idx] = \
                    self.location_is_whitespace_radioastronomy_only(region, (lat, lon))

####
#   END GENERAL WHITESPACE CALCULATIONS
####


####
#   TV STATION PROTECTION -- TABLE IMPLEMENTATIONS
####
    def get_tv_curve(self, is_digital):
        """
        Analog and digital TV stations use slightly different propagation models (the F(50,50) vs. the F(50,90) curves).
        This function returns the enum for the appropriate curve.

        :param is_digital: indicates whether the station is digital or analog
        :type is_digital: boolean
        :return: the propagation curve to use
        :rtype: :class:`PropagationCurve` member
        """
        if is_digital:
            return PropagationCurve.curve_50_90
        else:
            return PropagationCurve.curve_50_50

    def get_tv_target_field_strength_dBu(self, is_digital, freq):
        """
        TV stations have varying target field strengths depending on their assigned channel and whether they are digital
        or analog. This information can be found in section 15.712(a)(1) of the FCC's TVWS rules. This function simply
        implements the table found in that section.

        :param is_digital: indicates whether the station is digital or analog
        :type is_digital: bool
        :param freq: the center frequency of the station's channel
        :type freq: float
        :return: target field strength in dBu
        :rtype: float
        """
        if is_digital:
            if self._low_vhf_lower_frequency_mhz <= freq <= self._low_vhf_upper_frequency_mhz:
                return 28.0
            elif self._high_vhf_lower_frequency_mhz <= freq <= self._high_vhf_upper_frequency_mhz:
                return 66.0
            elif self._uhf_lower_frequency_mhz <= freq <= self._uhf_upper_frequency_mhz:
                return 41.0
            else:
                self.log.warning("Unsupported frequency: %d. Defaulting to UHF parameters." % freq)
                return 41.0
        else:
            if self._low_vhf_lower_frequency_mhz <= freq <= self._low_vhf_upper_frequency_mhz:
                return 47.0
            elif self._high_vhf_lower_frequency_mhz <= freq <= self._high_vhf_upper_frequency_mhz:
                return 56.0
            elif self._uhf_lower_frequency_mhz <= freq <= self._uhf_upper_frequency_mhz:
                return 64.0
            else:
                self.log.warning("Unsupported frequency: %d. Defaulting to UHF parameters." % freq)
                return 64.0

    def get_tv_cochannel_separation_distance_km(self, device_haat):
        """
        The cochannel separation distance mandated by the FCC depends on the whitespace device's height above average
         terrain (HAAT). The values are given in the table of section 15.712(a)(2) of the FCC's rules and the table
         is implemented in this function.

         .. note:: Values outside of the defined table (i.e. HAAT > 250 meters) will log a warning and return the value
         for 250 meters.

        :param device_haat: whitespace device's height above average terrain (HAAT) in meters
        :type device_haat: float
        :return: FCC-mandated cochannel separation distance in kilometers
        :rtype: float
        """
        if device_haat < 3:
            return 4.0
        elif 3 <= device_haat < 10:
            return 7.3
        elif 10 <= device_haat < 30:
            return 11.1
        elif 30 <= device_haat < 50:
            return 14.3
        elif 50 <= device_haat < 75:
            return 18.0
        elif 75 <= device_haat < 100:
            return 21.1
        elif 100 <= device_haat < 150:
            return 25.3
        elif 150 <= device_haat < 200:
            return 28.5
        elif 200 <= device_haat <= 250:
            return 31.2
        else:
            self.log.warning("Attempted to get TV cochannel separation distance for a device HAAT out of " +
                             "bounds: %.2f." % device_haat + "Reverting to value for largest valid HAAT.")
            return 31.2

    def get_tv_adjacent_channel_separation_distance_km(self, device_haat):
        """
        The adjacent channel separation distance mandated by the FCC depends on the whitespace device's height above
         average terrain (HAAT). The values are given in the table of section 15.712(a)(2) of the FCC's rules and the
         table is implemented in this function.

         .. note:: Values outside of the defined table (i.e. HAAT > 250 meters) will log a warning and return the value
         for 250 meters.

        :param device_haat: whitespace device's height above average terrain (HAAT) in meters
        :type device_haat: float
        :return: FCC-mandated adjacent channel separation distance in kilometers
        :rtype: float
        """
        if device_haat < 3:
            return 0.4
        elif 3 <= device_haat < 10:
            return 0.7
        elif 10 <= device_haat < 30:
            return 1.2
        elif 30 <= device_haat < 50:
            return 1.8
        elif 50 <= device_haat < 75:
            return 2.0
        elif 75 <= device_haat < 100:
            return 2.1
        elif 100 <= device_haat < 150:
            return 2.2
        elif 150 <= device_haat < 200:
            return 2.3
        elif 200 <= device_haat <= 250:
            return 2.4
        else:
            self.log.warning("Attempted to get TV adjacent channel separation distance for a device HAAT out of " +
                             "bounds: %.2f." % device_haat + "Reverting to value for largest valid HAAT.")
            return 2.4
####
#   END TV STATION PROTECTION -- TABLE IMPLEMENTATIONS
####

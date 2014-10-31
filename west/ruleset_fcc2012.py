from protected_entity_tv_station import ProtectedEntityTVStation
from protected_entity_radio_astronomy_site import ProtectedEntityRadioAstronomySite
from protected_entity_plmrs import ProtectedEntityPLMRS
from protected_entities_tv_stations import ProtectedEntitiesTVStations
from protected_entities_plmrs import ProtectedEntitiesPLMRS
from protected_entities_radio_astronomy_sites import ProtectedEntitiesRadioAstronomySites
from propagation_model_fcurves import PropagationModelFcurves
import helpers
from geopy.distance import vincenty
from propagation_model import PropagationCurve
from ruleset import Ruleset
import data_map


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
        return [ProtectedEntityTVStation, ProtectedEntityPLMRS,
                ProtectedEntityRadioAstronomySite]

    def get_default_propagation_model(self):
        return PropagationModelFcurves()


####
#   BASIC WHITESPACE CALCULATIONS
####
    def _is_permissible_channel(self, region, channel, device):
        """
        Checks that ``channel`` is permissible for whitespace operation by
        ``device``. In particular, returns False if:

          * ``channel`` is not a TVWS channel in the ``region`` or
          * ``device`` is portable and ``channel`` is not in the portable
            TVWS channel list for the ``region``

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :return: True if whitespace operation is allowed on this channel; \
            False otherwise
        :rtype: bool
        """
        if channel not in region.get_tvws_channel_list():
            return False

        if device.is_portable() and (channel not in
                                         region.get_portable_tvws_channel_list()):
            return False

        return True
####
#   END BASIC WHITESPACE CALCULATIONS
####

####
#   TV STATION PROTECTION CALCULATIONS
#   (separate section for protection tables)
####
    def get_tv_protected_radius_km(self, tv_station, device_location):
        """
        Determines the protected radius of the TV station in the direction of
        `device_location`.

        :param tv_station: the TV station of interest
        :type tv_station: \
            :class:`protected_entity_tv_station.ProtectedEntityTVStation`
        :param device_location: (latitude, longitude)
        :type device_location: tuple of floats
        :return: the protected radius of the TV station in kilometers
        :rtype: float
        """
        freq = tv_station.get_center_frequency()

        curve = self.get_tv_curve(tv_station.is_digital())
        target_field_strength_dbu = self.get_tv_target_field_strength_dBu(
            tv_station.is_digital(), freq)

        tv_location = tv_station.get_location()

        desired_watts = self._propagation_model.dBu_to_Watts(
            target_field_strength_dbu, freq)
        tv_power_watts = tv_station.get_erp_watts()
        pathloss_coefficient = desired_watts / tv_power_watts
        protection_distance_km = \
            self._propagation_model.get_distance(pathloss_coefficient,
                                                 frequency=freq,
                                                 tx_height=tv_station.get_haat_meters(),
                                                 tx_location=tv_location,
                                                 rx_location=device_location,
                                                 curve_enum=curve)
        return protection_distance_km

    def cochannel_tv_station_is_protected(self, tv_station, device_location,
                                          device_haat):
        """
        Determines whether or not the TV station is protected on a cochannel basis.

        .. note:: The device's proposed channel is not checked.

        .. warning:: Uses the TV station's bounding box (whose dimensions are \
            set in \
            :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`\
            ) to speed up computations. If these dimensions are too small, TV \
            stations will be erroneously excluded from this computation.

        :param tv_station:
        :type tv_station: \
            :class:`protected_entity_tv_station.ProtectedEntityTVStation`
        :param device_location: (latitude, longitude)
        :type device_location: tuple of floats
        :param device_haat: the height above average terrain (HAAT) of the \
            device in meters
        :type device_haat: float
        :return: True if the station is protected on a cochannel basis; False \
            otherwise
        :rtype: bool
        """

        if not tv_station.location_in_bounding_box(device_location):
            return False

        actual_distance_km = vincenty(tv_station.get_location(),
                                      device_location).kilometers
        protection_distance_km = self.get_tv_protected_radius_km(tv_station,
                                                                 device_location)
        separation_distance_km = \
            self.get_tv_cochannel_separation_distance_km(device_haat)

        # Check if we are inside the protected contour
        if actual_distance_km <= protection_distance_km + separation_distance_km:
            return True
        else:
            return False

    def adjacent_channel_tv_station_is_protected(self, tv_station,
                                                 device_location, device_haat):
        """
        Determines whether or not the TV station is protected on an
        adjacent-channel basis.

        .. note:: The device's proposed channel is not checked.

        .. warning:: Uses the TV station's bounding box (whose dimensions are \
            set in \
            :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`\
            ) to speed up computations. If these dimensions are too small, \
            TV stations will be erroneously excluded from this computation.

        :param tv_station:
        :type tv_station: \
            :class:`protected_entity_tv_station.ProtectedEntityTVStation`
        :param device_location: (latitude, longitude)
        :type device_location: tuple of floats
        :param device_haat: the height above average terrain (HAAT) of the \
            device in meters
        :type device_haat: float
        :return: True if the station is protected on an adjacent-channel \
            basis; False otherwise
        :rtype: bool
        """

        if not tv_station.location_in_bounding_box(device_location):
            return False

        actual_distance_km = vincenty(tv_station.get_location(), device_location).kilometers
        protection_distance_km = self.get_tv_protected_radius_km(tv_station, device_location)
        separation_distance_km = self.get_tv_adjacent_channel_separation_distance_km(device_haat)

        # Check if we are inside the protected contour
        return actual_distance_km <= (protection_distance_km + separation_distance_km)

    def location_is_whitespace_tv_stations_only(self, region, location, device_channel, device):
        """
        Determines whether a location is considered whitespace *on the basis
        of TV station protections alone.*

        .. note:: Does not check to see if the location is within the region.

        :param region: region containing the TV stations
        :type region: :class:`region.Region` object
        :param location: (latitude, longitude)
        :type location: tuple of floats
        :param device_channel: channel to be tested for whitespace
        :type device_channel: int
        :param device: device that proposes operating in the whitespaces
        :type device: :class:`device.Device`
        :return: True if the location is whitespace; False otherwise
        :rtype: bool
        """
        if device.is_portable():
            device_haat = 1
        else:
            device_haat = device.get_haat()

        tv_stations_container = region.get_protected_entities_of_type(
            ProtectedEntitiesTVStations, use_fallthrough_if_not_found=True)

        # Check cochannel exclusions
        cochannel_stations = tv_stations_container.get_list_of_entities_on_channel(device_channel)
        for station in cochannel_stations:
            if self.cochannel_tv_station_is_protected(station, location, device_haat):
                return False

        # Portable devices are not subject to adjacent-channel exclusions
        if device.is_portable():
            return True

        # Check adjacent-channel exclusions
        adjacent_channel_stations = []
        for adj_chan in [device_channel-1, device_channel+1]:
            if not adj_chan in region.get_channel_list():
                continue
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
        The separation distance mandated by the FCC depends on whether the
        PLMRS exclusion is a metropolitan region vs. an individual
        registration. It also depends on whether the proposed operation is
        cochannel or adjacent-channel. The values are given in section
        15.712(d) of the FCC's rules and the translation is implemented in this
        function.

         .. warning:: This function assumes that the proposed operation is \
            either cochannel or adjacent-channel. It does not check channel \
            assignments or proposals.

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
        Determines if a particular PLMRS entity is protected at the given
        location and on the specified channel.

        .. warning:: Uses the PLMRS entity's bounding box (whose dimensions \
            are set in \
            :class:`protected_entities_plmrs.ProtectedEntitiesPLMRS`) to \
            speed up computations. If these dimensions are too small, \
            PLMRS entities will be erroneously excluded from this computation.

        :param plmrs_entry: the PLMRS entity to be protected
        :type plmrs_entry: \
            :class:`protected_entity_plmrs.ProtectedEntityPLMRS` object
        :param location: (latitude, longitude)
        :type location: tuple of floats
        :param device_channel: channel to be tested for whitespace
        :type device_channel: int
        :param region: region containing the PLMRS entities
        :type region: :class:`region.Region` object
        :return: True if the PLMRS entity is protected; False otherwise
        :rtype: bool
        """
        if not plmrs_entry.location_in_bounding_box(location):
            return False

        plmrs_channel = plmrs_entry.get_channel()

        is_cochannel = (plmrs_channel == device_channel)

        # PLMRS is only protected on cochannel and first-adjacent
        # We know it's not protected if it's neither cochannel nor in a
        # first-adjacent channel
        if not is_cochannel and not helpers.channels_are_adjacent_in_frequency(
                region, plmrs_channel, device_channel):
            return False

        if not plmrs_entry.location_in_bounding_box(location):
            return False

        actual_distance_km = vincenty(plmrs_entry.get_location(), location).kilometers
        exclusion_radius_km = self.get_plmrs_exclusion_radius_km(plmrs_entry.is_metro(), is_cochannel)
        return actual_distance_km <= exclusion_radius_km

    def location_is_whitespace_plmrs_only(self, region, location, device_channel):
        """
        Determines whether a location is considered whitespace *on the basis
        of PLMRS protections alone.*

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
        plmrs_container = region.get_protected_entities_of_type(
            ProtectedEntitiesPLMRS, use_fallthrough_if_not_found=True)

        # Check cochannel exclusions
        cochannel_plmrs = plmrs_container.get_list_of_entities_on_channel(device_channel)
        for plmrs_entry in cochannel_plmrs:
            if self.plmrs_is_protected(plmrs_entry, location, device_channel, region):
                return False

        # Check adjacent-channel exclusions
        adjacent_channel_plmrs = []
        for adj_chan in [device_channel-1, device_channel+1]:
            if not adj_chan in region.get_channel_list():
                continue
            if helpers.channels_are_adjacent_in_frequency(region, adj_chan, device_channel):
                adjacent_channel_plmrs += plmrs_container.get_list_of_entities_on_channel(adj_chan)

        for plmrs_entry in adjacent_channel_plmrs:
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
        The radioastronomy separation distance mandated by the FCC is defined in
        section 15.712(h) of the FCC TVWS regulations. We include it as a
        parameter here to allow for easy modification.

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
        ras_container = region.get_protected_entities_of_type(
            ProtectedEntitiesRadioAstronomySites,
            use_fallthrough_if_not_found=True)
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

    def location_is_whitespace(self, region, location, channel, device):
        """
        Determines whether a location is considered whitespace, taking all
        protections into account (*except* wireless microphones).

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

        device_haat = device.get_haat()

        if not self._is_permissible_channel(region, channel, device):
            return False

        if not self.location_is_whitespace_tv_stations_only(region, location,
                                                            channel,
                                                            device_haat):
            return False

        if not self.location_is_whitespace_plmrs_only(region, location,
                                                      channel):
            return False

        if not self.location_is_whitespace_radioastronomy_only(region,
                                                               location):
            return False

        return True

    def apply_all_protections_to_map(self, region, is_whitespace_datamap2d,
                                     channel, device,
                                     ignore_channel_restrictions=False,
                                     reset_datamap=False, verbose=False):
        """
        Turns the input :class:`data_map.DataMap2D` into a map of whitespace
        availability. A value of `True` means that whitespace is available in
        that location, whereas a value of `False` means that that location is
        not considered whitespace for the supplied device.

        .. note:: Any entries which are already `False` will not be evaluated \
            unless `reset_datamap=True`.

        Recommended usage is to initialize is_whitespace_datamap2d to an
        is_in_region DataMap2D to avoid computations on locations which are
        outside of the region. No in-region testing is done otherwise.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_datamap2d: DataMap2D to be filled with the output
        :type is_whitespace_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :param ignore_channel_restrictions: if True, skips checks relating to \
            permissible channels of operation for the specified device
        :type ignore_channel_restrictions: bool
        :param reset_datamap: if True, the DataMap2D is reset to `True` \
            (i.e. "evaluate all") before computations begin
        :type reset_datamap: bool
        :param verbose: if True, progress updates will be logged \
            (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: None
        """
        if reset_datamap:
            # Initialize to True so that all points will be evaluated
            is_whitespace_datamap2d.reset_all_values(True)

        if not ignore_channel_restrictions:
            self.apply_channel_restrictions_to_map(region, is_whitespace_datamap2d, channel, device)

        self.apply_radioastronomy_exclusions_to_map(region, is_whitespace_datamap2d, verbose=verbose)
        self.apply_plmrs_exclusions_to_map(region, is_whitespace_datamap2d, channel, verbose=verbose)
        self.apply_tv_exclusions_to_map(region, is_whitespace_datamap2d, channel, device, verbose=verbose)

    def apply_entity_protections_to_map(self, region, is_whitespace_datamap2d,
                                        channel, device,
                                        protected_entities_list,
                                        ignore_channel_restrictions=False,
                                        reset_datamap=False, verbose=False):
        """
        Turns the input :class:`data_map.DataMap2D` into a map of whitespace
        availability `based on only the provided list of protected entities`. A
        value of `True` means that whitespace is available in that location,
        whereas a value of `False` means that that location is not considered
        whitespace for the supplied device.

        .. note:: Any entries which are already `False` will not be evaluated \
            unless `reset_datamap=True`.

        .. note:: Channel restrictions (see \
            :meth:`apply_channel_restrictions_to_map`) are still applied.

        .. note:: Logs an error but continues computation if an unrecognized \
            protected entity is found.

        Recommended usage is to initialize is_whitespace_datamap2d to an
        is_in_region DataMap2D to avoid computations on locations which are
        outside of the region. No in-region testing is done otherwise.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_datamap2d: DataMap2D to be filled with the output
        :type is_whitespace_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :param protected_entities_list: list of protected entities to be used \
            when calculating the whitespace map
        :type protected_entities_list: list of \
            :class:`protected_entities.ProtectedEntities` objects
        :param ignore_channel_restrictions: if True, skips checks relating to \
            permissible channels of operation for the specified device
        :type ignore_channel_restrictions: bool
        :param reset_datamap: if True, the DataMap2D is reset to `True` \
            (i.e. "evaluate all") before computations begin
        :type reset_datamap: bool
        :param verbose: if True, progress updates will be logged \
            (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: None
        """
        if reset_datamap:
            # Initialize to True so that all points will be evaluated
            is_whitespace_datamap2d.reset_all_values(True)

        if not ignore_channel_restrictions:
            self.apply_channel_restrictions_to_map(region, is_whitespace_datamap2d, channel, device)

        def update_function(latitude, longitude, latitude_index, longitude_index, currently_whitespace):
            if not currently_whitespace:       # already known to not be whitespace
                return None

            location = (latitude, longitude)

            # Check to see if any entity is protected
            location_is_whitespace = True
            for entity in protected_entities_list:
                if isinstance(entity, ProtectedEntityTVStation):
                    if channel == entity.get_channel():
                        location_is_whitespace &= \
                            not self.cochannel_tv_station_is_protected(entity, location, device.get_haat())
                    # Portable devices are not subjected to adjacent-channel exclusions
                    elif not device.is_portable() and \
                            helpers.channels_are_adjacent_in_frequency(region, entity.get_channel(), channel):
                        location_is_whitespace &= \
                            not self.adjacent_channel_tv_station_is_protected(entity, location, device.get_haat())
                    else:
                        # Not protected if not cochannel or adjacent channel
                        continue
                elif isinstance(entity, ProtectedEntityPLMRS):
                    if channel == entity.get_channel():
                        location_is_whitespace &= not self.plmrs_is_protected(entity, location, channel, region)
                elif isinstance(entity, ProtectedEntityRadioAstronomySite):
                    location_is_whitespace &= not self.radioastronomy_site_is_protected(entity, location)
                else:
                    self.log.error("Could not apply protections for the following entity: %s" % str(entity))
                    continue

                # Don't need to check other entities if the location has already been ruled out as whitespace
                if not location_is_whitespace:
                    break

            return location_is_whitespace

        is_whitespace_datamap2d.update_all_values_via_function(update_function, verbose=verbose)

    def apply_channel_restrictions_to_map(self, region,
                                          is_whitespace_datamap2d, channel, device):
        """
        Applies simple channel-based restrictions to the map. In particular,
        resets the :class:`data_map.DataMap2D` to False values if:

          * ``channel`` is not a TVWS channel in the ``region`` or
          * ``device`` is portable and ``channel`` is not in the portable
            TVWS channel list for the ``region``

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_datamap2d: DataMap2D to be filled with the output
        :type is_whitespace_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :return: None
        """
        if not self._is_permissible_channel(region, channel, device):
            is_whitespace_datamap2d.reset_all_values(False)

    def apply_tv_exclusions_to_map(self, region, is_whitespace_datamap2d,
                                   channel, device, verbose=False):
        """
        Applies TV exclusions to the given :class:`data_map.DataMap2D`.
        Entries will be marked `True` if they are whitespace and `False`
        otherwise.

        .. note:: Any entries which are already `False` will not be evaluated.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_datamap2d: DataMap2D to be filled with the output
        :type is_whitespace_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :param verbose: if True, progress updates will be logged \
            (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: None
        """
        def tv_station_update_function(latitude, longitude, latitude_index,
                                       longitude_index, currently_whitespace):
            if not currently_whitespace:       # already known to not be whitespace
                return None
            return self.location_is_whitespace_tv_stations_only(region,
                                                                (latitude,
                                                                 longitude),
                                                                channel,
                                                                device)

        if verbose:
            self.log.info("Applying TV exclusions")
        is_whitespace_datamap2d.update_all_values_via_function(tv_station_update_function, verbose=verbose)

    def apply_plmrs_exclusions_to_map(self, region, is_whitespace_datamap2d,
                                      channel, verbose=False):
        """
        Applies PLMRS exclusions to the given :class:`data_map.DataMap2D`.
        Entries will be marked `True` if they are whitespace and `False`
        otherwise.

        .. note:: Any entries which are already `False` will not be evaluated.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_datamap2d: DataMap2D to be filled with the output
        :type is_whitespace_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param verbose: if True, progress updates will be logged \
            (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: None
        """
        def plmrs_update_function(latitude, longitude, latitude_index,
                                  longitude_index, currently_whitespace):
            if not currently_whitespace:       # already known to not be whitespace
                return None
            return self.location_is_whitespace_plmrs_only(region, (latitude,
                                                                   longitude),
                                                          channel)

        if verbose:
            self.log.info("Applying PLMRS exclusions")
        is_whitespace_datamap2d.update_all_values_via_function(plmrs_update_function, verbose=verbose)

    def apply_radioastronomy_exclusions_to_map(self, region,
                                               is_whitespace_datamap2d,
                                               verbose=False):
        """
        Applies radioastronomy exclusions to the given
        :class:`data_map.DataMap2D`. Entries will be marked `True` if they
        are whitespace and `False` otherwise.

        .. note:: Any entries which are already `False` will not be evaluated.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_datamap2d: DataMap2D to be filled with the output
        :type is_whitespace_datamap2d: :class:`data_map.DataMap2D` object
        :param verbose: if True, progress updates will be logged \
            (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: None
        """
        def radioastronomy_update_function(latitude, longitude,
                                           latitude_index, longitude_index,
                                           currently_whitespace):
            if not currently_whitespace:       # already known to not be whitespace
                return None
            return self.location_is_whitespace_radioastronomy_only(region, (latitude, longitude))

        if verbose:
            self.log.info("Applying radioastronomy exclusions")
        is_whitespace_datamap2d.update_all_values_via_function(radioastronomy_update_function, verbose=verbose)

####
#   END GENERAL WHITESPACE CALCULATIONS
####

####
#   TV STATION PROTECTION -- TABLE IMPLEMENTATIONS
####
    def get_tv_curve(self, is_digital):
        """
        Analog and digital TV stations use slightly different propagation
        models (the F(50,50) vs. the F(50,90) curves). This function returns
        the enum for the appropriate curve.

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
        TV stations have varying target field strengths depending on their
        assigned channel and whether they are digital or analog. This
        information can be found in section 15.712(a)(1) of the FCC's TVWS
        rules. This function simply implements the table found in that
        section.

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
                return 36.0
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
        The cochannel separation distance mandated by the FCC depends on the
        whitespace device's height above average terrain (HAAT). The values
        are given in the table of section 15.712(a)(2) of the FCC's rules and
        the table is implemented in this function.

         .. note:: Values outside of the defined table (i.e. HAAT > 250 meters)\
            will log a warning and return the value for 250 meters.

        :param device_haat: whitespace device's height above average terrain \
            (HAAT) in meters
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
            self.log.warning("Attempted to get TV cochannel separation "
                             "distance for a device HAAT out of bounds: "
                             "%.2f." % device_haat + "Reverting to value for "
                                                     "largest valid HAAT.")
            return 31.2

    def get_tv_adjacent_channel_separation_distance_km(self, device_haat):
        """
        The adjacent channel separation distance mandated by the FCC depends
        on the whitespace device's height above average terrain (HAAT). The
        values are given in the table of section 15.712(a)(2) of the FCC's
        rules and the table is implemented in this function.

         .. note:: Values outside of the defined table (i.e. HAAT > 250 \
            meters) will log a warning and return the value for 250 meters.

        :param device_haat: whitespace device's height above average terrain \
            (HAAT) in meters
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
            self.log.warning("Attempted to get TV adjacent channel separation "
                             "distance for a device HAAT out of " + "bounds: "
                                                                    "%.2f." %
                             device_haat + "Reverting to value for largest "
                                           "valid HAAT.")
            return 2.4
####
#   END TV STATION PROTECTION -- TABLE IMPLEMENTATIONS
####

####
#   TV VIEWERSHIP CALCULATIONS
####

    def tv_station_is_viewable(self, tv_station, location):
        """
        Determines if a particular TV station is viewable at the given location.

        .. note:: The TV station's channel is not checked. It is assumed that \
            the TV station is on the channel of interest.

        .. warning:: Uses the TV station's bounding box (whose dimensions are \
            set in \
            :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`\
            ) to speed up computations. If these dimensions are too small, \
            TV stations will be erroneously excluded from this computation.
        """
        if not tv_station.location_in_bounding_box(location):
            return False

        actual_distance_km = vincenty(tv_station.get_location(),
                                      location).kilometers
        protection_distance_km = self.get_tv_protected_radius_km(tv_station,
                                                                 location)

        return actual_distance_km <= protection_distance_km

    def create_tv_viewership_datamap(self, region, is_in_region_datamap2d,
                                     channel, list_of_tv_stations=None,
                                     verbose=False):
        """
        Creates a :class:`data_map.DataMap2D` which is True (or truthy) where TV
        can be viewed and False elsewhere (including outside the region). If not
        specified, the list of TV stations is taken from ``region``. If
        specified, only the TV stations in the list are considered.

        The output DataMap2D properties will be taken from
        ``is_in_region_datamap2d``. No input data is modified in this
        calculation.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_in_region_datamap2d: DataMap2D which has value True (or a \
            truthy value) inside the region's boundary and False outside. This \
            is purely to speed up computations by skipping locations that do \
            not matter.
        :type is_in_region_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for viewership
        :type channel: int
        :param verbose: if True, progress updates will be logged \
            (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: datamap holding values representing TV viewership
        :rtype: :class:`data_map.DataMap2D`
        """

        viewership_map = data_map.DataMap2D.get_copy_of(is_in_region_datamap2d)
        viewership_map.reset_all_values(0)

        # Use the TV stations from the region if no list is provided
        if list_of_tv_stations is None:
            all_tv_stations = region.get_protected_entities_of_type(ProtectedEntitiesTVStations)
            list_of_tv_stations = all_tv_stations.get_list_of_entities_on_channel(channel)

        def tv_station_viewership_update_function(latitude, longitude,
                                                  latitude_index,
                                                  longitude_index,
                                                  currently_viewable):
            """Returns True if TV can be viewed at this location and False
            otherwise. Returns None if the location is already listed as
            viewable."""
            if not is_in_region_datamap2d.get_value_by_index(latitude_index,
                                                             longitude_index):
                return False        # outside of the US is defined as not viewable
            if currently_viewable:
                return None         # don't update if it is already known that TV is viewable at this location

            for station in list_of_tv_stations:
                if not station.get_channel() == channel:
                    continue
                if self.tv_station_is_viewable(station, (latitude, longitude)):
                    return True

            return False

        viewership_map.update_all_values_via_function(tv_station_viewership_update_function, verbose=verbose)
        return viewership_map

####
#   END TV VIEWERSHIP CALCULATIONS
####

from data_map import DataMap2D
from propagation_model import InvalidDistanceError
from abc import abstractmethod
from geopy.distance import vincenty


class DataMap2DSignalStrength(DataMap2D):
    """
    A :class:`data_map.DataMap2D` specialized for computing combined signal
    strengths.
    """

    @abstractmethod
    def combine_values(self, existing_value, new_value):
        """
        Defines how values should be combined. For example: sum(), max(), or
        min() may be used. The combined value should be returned.
        """
        return

    def should_skip_pixel(self, latitude, longitude, latitude_index,
                          longitude_index, current_pixel_value):
        """
        By default, the computation engine will not skip any pixels.
        Override this function to change that functionality.

        If True is returned, computation for that pixel will be skipped.
        """
        return False


    def add_tv_stations(self, list_of_tv_stations, pathloss_function,
                        verbose=False):
        """
        The pathloss function should have all but the station-specific
        parameters specified. Use lambdas.

        ALL stations are considered, regardless of e.g. channel (but the
        pathloss function will use the appropriate frequency, etc.).

        In some cases, it may be necessary to use a lambda instead of the raw
        pathloss function. For example::

            pm = PropagationModelFcurvesWithoutTerrain()
            pl_function = lambda *args, **kwargs: pm.get_pathloss_coefficient(*args, curve_enum=PropagationCurve.curve_50_90, **kwargs)
            my_signal_map.add_tv_stations(my_tv_stations, pathloss_function=pl_function)

        .. warning:: the signal strength will not be calculated outside the \
        station's bounding box in order to save on computations.

        .. warning:: any InvalidDistanceErrors from the propagation model will \
        be ignored and the signal strength at that location (for that station) \
        will be zero.

        :param list_of_tv_stations: list of \
        :class:`protected_entity_tv_station.ProtectedEntityTvStation` objects
        :param pathloss_function: the pathloss function to be used when \
        calculating the signal strength for a single transmitter, e.g. \
         :meth:`propagation_model_fcurves.get_pathloss_coefficient`
        :param verbose: if True, progress updates will be logged (level = \
        INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return:
        """

        def update_signal_strengths(latitude, longitude, latitude_index,
                                    longitude_index, current_value):
            location = (latitude, longitude)
            if self.should_skip_pixel(latitude, longitude, latitude_index,
                                      longitude_index, current_value):
                return None

            for tv_station in list_of_tv_stations:

                station_signal_strength = self._get_station_signal_strength(
                    location, tv_station, pathloss_function)

                return self.combine_values(current_value,
                                           station_signal_strength)

        self.update_all_values_via_function(update_signal_strengths,
                                            verbose=verbose)

    def _get_station_signal_strength(self, location, tv_station,
                                     pathloss_function):
        if not tv_station.location_in_bounding_box(location):
            return 0

        tv_location = tv_station.get_location()
        distance_km = vincenty(tv_location, location).kilometers
        freq = tv_station.get_center_frequency()
        try:
            pathloss = pathloss_function(distance_km, frequency=freq,
                                         tx_height=tv_station.get_haat_meters(),
                                         rx_height=None,
                                         tx_location=tv_location,
                                         rx_location=location)
            # TODO: account for rx height?
        except InvalidDistanceError:
            return 0

        return tv_station.get_erp_watts() * pathloss


class DataMap2DSignalStrengthMax(DataMap2DSignalStrength):
    """
    This class helps to create a map which contains the MAXIMUM signal
    strength across all entities at any given location.

    Pixels which have a negative value will be skipped by default.
    """
    def combine_values(self, existing_value, new_value):
        return max(existing_value, new_value)

    def should_skip_pixel(self, latitude, longitude, latitude_index,
                          longitude_index, current_pixel_value):
        return current_pixel_value < 0


class DataMap2DSignalStrengthSum(DataMap2DSignalStrength):
    """
    This class helps to create a map which contains the SUM of signal
    strengths across all entities at any given location.

    Pixels which have a negative value will be skipped by default.
    """

    def combine_values(self, existing_value, new_value):
        return existing_value + new_value

    def should_skip_pixel(self, latitude, longitude, latitude_index,
                          longitude_index, current_pixel_value):
        return current_pixel_value < 0

from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger


class InvalidDistanceError(Exception):
    pass


class PropagationCurve(object):
    """
    This class is a poor-man's enum because Python 2 does not support the Enum class.
    """

    @classmethod
    @property
    def curve_50_10(cls):
        """Field strength exceeded at 50% of the locations at least 10% of the time."""
        return 0

    @classmethod
    @property
    def curve_50_50(cls):
        """Field strength exceeded at 50% of the locations at least 50% of the time."""
        return 0

    @classmethod
    @property
    def curve_50_90(cls):
        """Field strength exceeded at 50% of the locations at least 90% of the time."""
        return 0


class PropagationModel(object):
    """This class defines the interface for all PropagationModels."""

    __metaclass__ = ABCMeta

    def __init__(self):
        self.log = getModuleLogger(self)

    def get_pathloss_coefficient(self, distance, frequency=None, tx_height=None, rx_height=None, tx_location=None,
                                 rx_location=None, curve_enum=None):
        """
        Computes the pathloss coefficient given a distance.

        Identical to :meth:`get_pathloss_coefficient_unchecked` but includes input validation.

          * For rare computations, use :meth:`get_pathloss_coefficient` alone.
          * For repeated computations where efficiency is key, use :meth:`parameters_are_sufficient` and
            :meth:`get_pathloss_coefficient_unchecked`.


        :param distance: distance between the transmitter and receiver (kilometers)
        :type distance: float
        :param frequency: the center frequency for transmission (MHz)
        :type frequency: float
        :param tx_height: the height or HAAT of the transmitter (meters)
        :type tx_height: float
        :param rx_height: the height or HAAT of the receiver (meters)
        :type rx_height: float
        :param tx_location: (latitude, longitude) (decimal degrees)
        :type tx_location: tuple of floats
        :param rx_location: (latitude, longitude) (decimal degrees)
        :type rx_location: tuple of floats
        :param curve_enum: the propagation curve to use
        :type curve_enum: :class:`PropagationCurve` member
        :return: pathloss coefficient
        :rtype: float
        """
        has_all_params, error_message = self._has_required_parameters(frequency, tx_height, rx_height, tx_location,
                                                                      rx_location, curve_enum)
        if not has_all_params:
            raise AttributeError("Missing one or more required parameters: %s" % error_message)

        self._raise_error_if_input_invalid(frequency, tx_height, rx_height, tx_location, rx_location, curve_enum,
                                           distance=distance)

        return self.get_pathloss_coefficient_unchecked(distance=distance,
                                                       frequency=frequency, tx_height=tx_height, rx_height=rx_height,
                                                       tx_location=tx_location, rx_location=rx_location,
                                                       curve_enum=curve_enum)

    @abstractmethod
    def get_pathloss_coefficient_unchecked(self, distance, frequency=None, tx_height=None, rx_height=None,
                                           tx_location=None, rx_location=None, curve_enum=None):
        """
        Computes the pathloss coefficient given a distance.

        Identical to :meth:`get_pathloss_coefficient` but skips input validation (including the check for necessary
        parameters). However, this will increase efficiency in cases where the function is called repeatedly. In that
        case, it is recommended to use :meth:`parameters_are_sufficient` first to ensure that the necessary parameters will
        be provided.

          * For rare computations, use :meth:`get_pathloss_coefficient` alone.
          * For repeated computations where efficiency is key, use :meth:`parameters_are_sufficient` and
            :meth:`get_pathloss_coefficient_unchecked`.


        :param distance: distance between the transmitter and receiver (kilometers)
        :type distance: float
        :param frequency: the center frequency for transmission (MHz)
        :type frequency: float
        :param tx_height: the height or HAAT of the transmitter (meters)
        :type tx_height: float
        :param rx_height: the height or HAAT of the receiver (meters)
        :type rx_height: float
        :param tx_location: (latitude, longitude) (decimal degrees)
        :type tx_location: tuple of floats
        :param rx_location: (latitude, longitude) (decimal degrees)
        :type rx_location: tuple of floats
        :param curve_enum: the propagation curve to use
        :type curve_enum: :class:`PropagationCurve` member
        :return: pathloss coefficient
        :rtype: float
        """

    def get_distance(self, pathloss_coefficient, frequency=None, tx_height=None, rx_height=None, tx_location=None,
                     rx_location=None, curve_enum=None):
        """
        Given a pathloss coefficient, returns the distance.

        Identical to :meth:`get_distance_unchecked` but includes input validation.

          * For rare computations, use :meth:`get_distance` alone.
          * For repeated computations where efficiency is key, use :meth:`parameters_are_sufficient` and
            :meth:`get_distance_unchecked`.

        :param pathloss_coefficient: pathloss coefficient (e.g. from :meth:`get_pathloss_coefficient`
        :type pathloss_coefficient: float
        :param frequency: the center frequency for transmission (MHz)
        :type frequency: float
        :param tx_height: the height or HAAT of the transmitter (meters)
        :type tx_height: float
        :param rx_height: the height or HAAT of the receiver (meters)
        :type rx_height: float
        :param tx_location: (latitude, longitude) (decimal degrees)
        :type tx_location: tuple of floats
        :param rx_location: (latitude, longitude) (decimal degrees)
        :type rx_location: tuple of floats
        :param curve_enum: the propagation curve to use
        :type curve_enum: :class:`PropagationCurve` member
        :return: distance (kilometers)
        :rtype: float
        """

        has_all_params, error_message = self._has_required_parameters(frequency, tx_height, rx_height, tx_location,
                                                                      rx_location, curve_enum)
        if not has_all_params:
            raise AttributeError("Missing one or more required parameters: %s" % error_message)

        self._raise_error_if_input_invalid(frequency, tx_height, rx_height, tx_location, rx_location, curve_enum,
                                           pathloss_coefficient=pathloss_coefficient)

        return self.get_distance_unchecked(pathloss_coefficient=pathloss_coefficient,
                                           frequency=frequency, tx_height=tx_height, rx_height=rx_height,
                                           tx_location=tx_location, rx_location=rx_location,
                                           curve_enum=curve_enum)

    @abstractmethod
    def get_distance_unchecked(self, pathloss_coefficient, frequency=None, tx_height=None, rx_height=None, tx_location=None, rx_location=None, curve_enum=None):
        """
        Given a pathloss coefficient, returns the distance.

        Identical to :meth:`get_distance` but skips input validation (including the check for necessary
        parameters). However, this will increase efficiency in cases where the function is called repeatedly. In that
        case, it is recommended to use :meth:`parameters_are_sufficient` first to ensure that the necessary parameters will
        be provided.

          * For rare computations, use :meth:`get_distance` alone.
          * For repeated computations where efficiency is key, use :meth:`parameters_are_sufficient` and
            :meth:`get_distance_unchecked`.

        :param pathloss_coefficient: pathloss coefficient (e.g. from :meth:`get_pathloss_coefficient`
        :type pathloss_coefficient: float
        :param frequency: the center frequency for transmission (MHz)
        :type frequency: float
        :param tx_height: the height or HAAT of the transmitter (meters)
        :type tx_height: float
        :param rx_height: the height or HAAT of the receiver (meters)
        :type rx_height: float
        :param tx_location: (latitude, longitude) (decimal degrees)
        :type tx_location: tuple of floats
        :param rx_location: (latitude, longitude) (decimal degrees)
        :type rx_location: tuple of floats
        :param curve_enum: the propagation curve to use
        :type curve_enum: :class:`PropagationCurve` member
        :return: distance (kilometers)
        :rtype: float
        """
        return

    @abstractmethod
    def requires_terrain(self):
        """Returns a boolean specifying whether or not this propagation model
        requires terrain information."""
        return

    @abstractmethod
    def requires_tx_height(self):
        """Returns a boolean specifying whether or not this propagation
        model requires transmitter height information."""
        return

    @abstractmethod
    def requires_rx_height(self):
        """Returns a boolean specifying whether or not this propagation
        model requires receiver height information."""
        return

    @abstractmethod
    def requires_frequency(self):
        """Returns a boolean specifying whether or not this propagation
        model requires frequency information."""
        return

    @abstractmethod
    def requires_tx_location(self):
        """Returns a boolean specifying whether or not this propagation
        model requires the transmitter's location."""
        return

    @abstractmethod
    def requires_rx_location(self):
        """Returns a boolean specifying whether or not this propagation
        model requires the receiver's location."""
        return

    @abstractmethod
    def requires_curve_enum(self):
        """Returns a boolean specifying whether or not this propagation
        model requires the specification of a propagation curve (see
        :class:`PropagationCurve`)."""
        return


    def parameters_are_sufficient(self, provides_terrain=False, provides_tx_height=False, provides_rx_height=False,
                                  provides_tx_location=False, provides_rx_location=False, provides_frequency=False,
                                  provides_curve_enum=False):
        """
        Checks to see if the provided parameters are sufficient for use with this propagation model. This function is
        intended as a pre-check by algorithms which will use :meth:`get_pathloss_coefficient_unchecked` or
        :meth:`get_distance_unchecked`, as a balance between catching errors and efficiency.

        Each parameter is boolean, specifying whether or not the algorithm intends to specify the corresponding
        parameter when calling :meth:`get_pathloss_coefficient_unchecked`.

        :param provides_terrain:
        :param provides_tx_height:
        :param provides_rx_height:
        :param provides_tx_location:
        :param provides_rx_location:
        :param provides_frequency:
        :param provides_curve_enum:
        :return: True if all necessary parameters are provided; False otherwise
        :rtype: boolean
        """
        if self.requires_terrain() and not provides_terrain:
            return False

        if self.requires_tx_height() and not provides_tx_height:
            return False

        if self.requires_rx_height() and not provides_rx_height:
            return False

        if self.requires_tx_location() and not provides_tx_location:
            return False

        if self.requires_rx_location() and not provides_rx_location:
            return False

        if self.requires_frequency() and not provides_frequency:
            return False

        if self.requires_curve_enum() and not provides_curve_enum:
            return False

        return True


    def _has_required_parameters(self, frequency, tx_height, rx_height, tx_location, rx_location, curve_enum):
        """
        Checks to see if required input parameters have been specified. Does not check values or types. Checks that
        the length of a location parameter (if required) is exactly 2.

        :return: True if all required parameters are present; False otherwise
        :rtype: boolean
        """
        if self.requires_frequency() and frequency is None:
            return False, "missing frequency"

        if self.requires_tx_height() and tx_height is None:
            return False, "missing transmitter height"

        if self.requires_rx_height() and rx_height is None:
            return False, "missing receiver height"

        if self.requires_tx_location() and (tx_location is None or len(tx_location) is not 2):
            return False, "missing or invalid transmitter location"

        if self.requires_rx_location() and (rx_location is None or len(rx_location) is not 2):
            return False, "missing or invalid receiver location"

        if self.requires_curve_enum() and curve_enum is None:
            return False, "missing curve enum"

        return True, None

    def _raise_error_if_input_invalid(self, frequency, tx_height, rx_height, tx_location, rx_location, curve_enum,
                                      distance=None, pathloss_coefficient=None):
        """
        This function is meant to be overridden by derived classes if customized behavior is desired. This documentation
        describes its intended behavior but by default does nothing.

        Checks to see if the required input parameters are in a valid range. Raises ValueError.
        """
        return

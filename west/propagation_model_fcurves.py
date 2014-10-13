from propagation_model import PropagationModel, PropagationCurve, \
    InvalidDistanceError
from configuration import package_directory
from ctypes import *
import os.path
from math import log10


class PropagationModelFcurves(PropagationModel):
    """The FCC's F-curves model.

    This model uses the FCC's Fortran code which can be downloaded from
    http://www.fcc.gov/mb/audio/bickel/archive/fmtvcurves.zip. Some modifications were made in order to compile the code.
    However, functionality should not be changed by these modifications. See below for a list of them. To learn more
    about the F-curves, see the following:

      * http://transition.fcc.gov/Bureaus/Mass_Media/Databases/documents_collection/rptRS76-01.pdf
      * http://transition.fcc.gov/oet/info/documents/reports/R-6602.pdf

    **To compile the Fortran code for use with this class, use the following command**::

        gfortran -std=legacy -shared -o curves_subroutines.so curves_subroutines.f

    **Some general notes on using this class:**
      * Maximum distance: 300 km

         * An error is generated if using a greater distance

      * Minimum distance (without using free-space calculations): 1.5 km

         * A warning is generated if using free-space calculations

      * Only certain frequencies are supported:

         * Supported frequencies:

             * 54 - 88 MHz (US lower VHF: channels 2-6)
             * 174 - 216 MHz (US upper VHF: channels 7-13)
             * 470 - 890 MHz (US UHF: channels 14-84)

         * A ValueError is raised if using an unsupported frequency.
         * There are no actual code-based limitations on these frequencies, only model-imposed limitations (i.e. the
            F-curves were not designed for frequencies outside these ranges). Modification, although undefined, would
            require only a small change in the Python code.

      * The default output of the F-curve library is dBu. This is converted to a pathloss coefficient in this class.

    **Modifications to Fortran code:**
      * The Fortran code was written using linear indexing into a 2-D array. This is not supported in later versions of
        Fortran and thus the code must be modified before it will run without producing a segmentation fault. In
        particular, the subroutine ITPLBV (which performs bivariate interpolation) must be updated via the following
        steps:

         * Download the original Fortran code
         * Replace the ITPLBV subroutine in curves_subroutines.f with the one found in itplbv_updated.f

            * Note that the updated code contains a commented version of the original code (as of this writing) for
              reference.

         * Thanks goes to the commenters at
           http://compgroups.net/comp.lang.fortran/passing-c++-array-to-fortran-function/594289

      * There also appears to be an error with the size of some arrays which produces a Fortran compiler warning. It
        appears to be safe to ignore these warnings but to fix them, do the following:

         * Navigate to the subroutine `f5090` in curves_subroutines.f
         * Replace the number 201 with the number 1000 for the following variables:

            * fs
            * d
            * h
            * n_points

    **To run the original F-curve program using f2c** (not buggy)::

        f2c curves_subroutines.f
        f2c curves.f
        gcc -o curves curves.c curves_subroutines.c -lm -lf2c
        ./curves

    **To run the Fortran program using only gfortran** (buggy)::

        gfortran -std=legacy -o curves curves.f curves_subroutines.f
        ./curves
    """

    def __init__(self, *args, **kwargs):
        super(PropagationModelFcurves,self).__init__(*args, **kwargs)

        self._initialize_fcurve_library_and_function()
        self._initialize_error_codes()

    # The F-curve results for frequencies within a given range (e.g. high VHF) will be identical. However, the F-curve
    # program requires input in terms of channel number. Here, we define each range and its corresponding proxy channel
    # number. The actual proxy channel number does not change the results as long as it is within the range (e.g. 7-13).
    #
    # A similar process can be seen in lines 368 - 388 of curves.f. curves.f provides a human interface (command-line
    # prompt) to curves_subroutines.f contains the actual computations.
    #
    # Source for frequencies: http://en.wikipedia.org/wiki/North_American_television_frequencies#Channel_frequencies
    #
    # Note however that the frequency input to the pathloss model *does* matter in that it will change the results of
    # the dBu -> dBm conversion that happens after the F-curves calculation. It is assumed that the channel's center
    # frequency is provided.
    #
    # Change these variables only at your own risk.
    _low_vhf_lower_frequency_mhz = 54   # US channel 2 (lower edge)
    _low_vhf_upper_frequency_mhz = 88   # US channel 6 (upper edge)
    _low_vhf_proxy_channel = 3

    _high_vhf_lower_frequency_mhz = 174  # US channel 7 (lower edge)
    _high_vhf_upper_frequency_mhz = 216  # US channel 13 (upper edge)
    _high_vhf_proxy_channel = 9

    _uhf_lower_frequency_mhz = 470      # US channel 14 (lower edge)
    _uhf_upper_frequency_mhz = 890      # US channel 83 (upper edge)
    _uhf_proxy_channel = 20

    def _raise_error_if_input_invalid(self, frequency, tx_height, rx_height, tx_location, rx_location, curve_enum,
                                      distance=None, pathloss_coefficient=None):
        if (not (self._low_vhf_lower_frequency_mhz <= frequency <= self._low_vhf_upper_frequency_mhz)
                and not (self._high_vhf_lower_frequency_mhz <= frequency <= self._high_vhf_upper_frequency_mhz)
                and not (self._uhf_lower_frequency_mhz <= frequency <= self._uhf_upper_frequency_mhz)):
            raise ValueError(self._unsupported_frequency_value_string(frequency))

        if distance is not None and distance > 300:
            raise InvalidDistanceError("Unsupported distance: %.2f (maximum: "
                                       "300 km)." % distance)

####
#   LIBRARY FUNCTIONS
####
    def _initialize_fcurve_library_and_function(self):
        shared_object_path = os.path.join(package_directory, "propagation_models", "fcurves", "curves_subroutines.so")
        cdll.LoadLibrary(shared_object_path)
        fcurves_lib = CDLL(shared_object_path)
        self._initialize_library_functions(fcurves_lib)

    def _initialize_library_functions(self, fcurves_lib):
        # F(50,50) and F(50,10)
        # See lines 1873 - 1941 of curves_subroutines.f for documentation
        # self._tvfmfs_metric = fcurves_lib.tvfmfs_metric__
        self._tvfmfs_metric = fcurves_lib.tvfmfs_metric_
        self._tvfmfs_metric.restype = c_int
        self._tvfmfs_metric.argtypes = [POINTER(c_float),           # ERP (kW)
                                        POINTER(c_float),           # HAAT (meters)
                                        POINTER(c_long),            # channel (FM or TV channel number)
                                        POINTER(c_float),           # field strength (dBu)
                                        POINTER(c_float),           # distance (km)
                                        POINTER(c_long),            # switch (1 = field strength given distance,
                                                                    #         2 = distance, given field strength)
                                        POINTER(c_long),            # curve (0 = F(50,50), 1 = F(50,10)
                                        POINTER(c_byte * 2), c_long]    # error flag

        # F(50,90)
        # See lines 97 - 130 of curves_subroutines.f for documentation
        # self._f5090 = fcurves_lib.f5090_
        self._f5090 = fcurves_lib.f5090_
        self._f5090.restype = c_int
        self._f5090.argtypes = [POINTER(c_float),                   # ERP (kW)
                                POINTER(c_float),                   # HAAT (meters)
                                POINTER(c_long),                    # input channel (??)
                                POINTER(c_float),                   # field (field strength in dBu)
                                POINTER(c_float),                   # distance (km)
                                POINTER(c_long),                    # ichoise (1 = field strength given distance,
                                                                    #          2 = distance, given field strength)
                                POINTER(c_byte * 2), c_long]        # error flag
####
#   END LIBRARY FUNCTIONS
####




####
#   F-CURVE FLAG FUNCTIONS
####
    def _initialize_error_codes(self):
        """
        The library sets various flag values depending on the error (if any). Original error/warning code definitions
        can be found on lines 1918 - 1939 of fcurves_subroutines.f.

        :return: None
        """

        # Original error/warning code definitions can be found on lines 1918 - 1939 of fcurves_subroutines.f
        self._error_codes = {
            "A2": "DISTANCE EXCEEDS GREATEST VALUE ON CURVES.",
            "A3": "INVALID CHANNEL NUMBER.",
            "A4": "INVALID CURVE SELECTED.",
            "A5": "INVALID SWITCH VALUE.",
            "A6": "ERP LESS THAN OR EQUAL TO 0 KILOWATTS.",
            "A9": "INVALID 'DISTANCE' VALUE FOR SWITCH = 1.",
            "  ": None
        }
        self._invalid_distance_errors = ["A2"]

        self._warning_codes = {
            "A1": "FREE SPACE EQUATION USED TO FIND REQUESTED ARGUMENT.",
            "A7": "HAAT LESS THAN 30 METERS, SET TO 30 METERS.",
            "A8": "HAAT EXCEEDS 1600 METERS, SET TO 1600 METERS.",
            "  ": None
        }

    def _raise_warning_or_error_if_flag_set(self, flag):
        """
        Checks the flag for any of the error codes defined in :meth:`_initialize_error_codes` and raises an Exception or
        Warning depending on the type of flag. If the flag indicates success, no Exception or Warning is raised.

        :param flag: two-character flag from the F-curve library
        :type flag: c_byte * 2
        :return: None
        """
        flag = self._flag_to_string(flag)

        if flag not in self._error_codes and flag not in self._warning_codes:
            raise KeyError("Unknown flag returned: '%s'" % flag)

        if flag in self._error_codes:
            if flag in self._invalid_distance_errors:
                raise InvalidDistanceError("Invalid distance for propagation "
                                           "model %r" % self)

            error_message = self._error_codes[flag]

            if error_message is None:
                return
            else:
                raise Exception("F-curve error: %s" % error_message)
        else:
            warning_message = self._warning_codes[flag]
            if warning_message is None:
                return
            else:
                #raise Warning("F-curve warning: %s" % warning_message)
                # self.log.warn("F-curve warning: %s" % warning_message)  # TODO: should this be a real warning?
                pass

    def _flag_to_string(self, flag):
        """
        Converts the flag into an ASCII string.

        :param flag: two-character flag from the F-curve library
        :type flag: c_byte * 2
        :return: ASCII version of the flag
        :rtype: str
        """
        return str(unichr(flag[0]) + unichr(flag[1]))
####
#   END F-CURVE FLAG FUNCTIONS
####

####
#   UNIT CONVERSION FUNCTIONS
####
    def _unsupported_frequency_value_string(self, frequency):
        """
        Generates a string to be used if an unsupported frequency has been encountered. This string includes the
        supported frequency ranges to assist the user.

        :param frequency: unsupported frequency
        :type frequency: float or integer
        :return:
        :rtype: string
        """
        return "Unsupported frequency: %2.2f. Valid ranges are: [%.1f, %.1f], [%.1f, %.1f], and [%.1f, %.1f] MHz." % \
            (frequency,
             self._low_vhf_lower_frequency_mhz, self._low_vhf_upper_frequency_mhz,
             self._high_vhf_lower_frequency_mhz, self._high_vhf_upper_frequency_mhz,
             self._uhf_lower_frequency_mhz, self._uhf_upper_frequency_mhz)

    def _get_proxy_channel_number(self, frequency):
        """
        Converts the frequency into a proxy channel (see comments above explaining the use of proxy channels).

        Raises a ValueError if the frequency is unsupported.

        :param frequency:
        :type frequency: float or integer
        :return: proxy channel
        :rtype: integer
        """
        if self._low_vhf_lower_frequency_mhz <= frequency <= self._low_vhf_upper_frequency_mhz:
            return self._low_vhf_proxy_channel
        elif self._high_vhf_lower_frequency_mhz <= frequency <= self._high_vhf_upper_frequency_mhz:
            return self._high_vhf_proxy_channel
        elif self._uhf_lower_frequency_mhz <= frequency <= self._uhf_upper_frequency_mhz:
            return self._uhf_proxy_channel
        else:
            raise ValueError(self._unsupported_frequency_value_string(frequency))

    def dBu_to_dBm(self, dBu, frequency):
        """
        Converts dBu to dBm
        based on http://transition.fcc.gov/Bureaus/Engineering_Technology/Documents/bulletins/oet69/oet69.pdf

        :param dBu:
        :param frequency: center frequency of the band
        :return: the value in dBm
        :rtype: float
        """
        if self._low_vhf_lower_frequency_mhz <= frequency <= self._low_vhf_upper_frequency_mhz:
            return dBu - 111.8
        elif self._high_vhf_lower_frequency_mhz <= frequency <= self._high_vhf_upper_frequency_mhz:
            return dBu - 120.8
        elif self._uhf_lower_frequency_mhz <= frequency <= self._uhf_upper_frequency_mhz:
            return dBu - 130.8 + 20*log10(float(615)/frequency)
        else:
            raise ValueError(self._unsupported_frequency_value_string(frequency))

    def dBm_to_Watts(self, dBm):
        """
        Unit conversion from dBm to Watts.

        :param dBm:
        :return: the value in Watts
        :rtype: float
        """
        return 1e-3*10**(float(dBm)/10)

    def Watts_to_dBm(self, watts):
        """
        Unit conversion from Watts to dBm.

        :param watts:
        :return: the value in dBm
        :rtype: float
        """
        return 10*log10(1e3*float(watts))

    def Watts_to_dBu(self, watts, frequency):
        """
        Unit conversion from Watts to dBu. See :meth:`dBm_to_dBu` for any important disclaimers.

        :param watts:
        :param frequency:
        :return:
        """
        dBm = self.Watts_to_dBm(watts)
        return self.dBm_to_dBu(dBm, frequency)

    def dBu_to_Watts(self, dBu, frequency):
        """
        Unit conversion from dBu to Watts. See :meth:`dBu_to_dBm` for any important disclaimers.

        :param dBu:
        :param frequency:
        :return:
        """
        dBm = self.dBu_to_dBm(dBu, frequency)
        return self.dBm_to_Watts(dBm)


    def dBm_to_dBu(self, dBm, frequency):
        """
        Converts dBm to dBu
        based on http://transition.fcc.gov/Bureaus/Engineering_Technology/Documents/bulletins/oet69/oet69.pdf

        :param dBm:
        :param frequency: center frequency of the band
        :return: the value in dBu
        :rtype: float
        """
        # Source: http://transition.fcc.gov/Bureaus/Engineering_Technology/Documents/bulletins/oet69/oet69.pdf
        if self._low_vhf_lower_frequency_mhz <= frequency <= self._low_vhf_upper_frequency_mhz:
            return dBm + 111.8
        elif self._high_vhf_lower_frequency_mhz <= frequency <= self._high_vhf_upper_frequency_mhz:
            return dBm + 120.8
        elif self._uhf_lower_frequency_mhz <= frequency <= self._uhf_upper_frequency_mhz:
            return dBm + 130.8 - 20*log10(float(615)/frequency)
        else:
            raise ValueError(self._unsupported_frequency_value_string(frequency))
####
#   END UNIT CONVERSION FUNCTIONS
####


    def _get_curve_integer(self, curve_enum):
        if curve_enum is None:
            raise AttributeError("No curve specified.")
        elif curve_enum == PropagationCurve.curve_50_50:
            return 0
        elif curve_enum == PropagationCurve.curve_50_10:
            return 1
        elif curve_enum == PropagationCurve.curve_50_90:
            return 2
        else:
            raise ValueError("No curve associated with '%s'. Please see the PropagationCurve class for options." % str(curve_enum))

    def get_pathloss_coefficient_unchecked(self, distance, frequency=None, tx_height=None, rx_height=None, tx_location=None, rx_location=None, curve_enum=None):
        erp = c_float(1e-3)     # 1 W (.001 kW)         DO NOT CHANGE
        haat = c_float(self._get_haat(tx_height, tx_location, rx_location))   # meters
        channel = c_long(self._get_proxy_channel_number(frequency))
        distance = c_float(distance)        # km
        curve = c_long(self._get_curve_integer(curve_enum))
        switch = c_long(1)      # 1 = compute field strength from distance
                                # 2 = compute distance from field strength

        field_strength_dbu = c_float(-1)   # this will hold the output
        flag = (c_byte*2)(ord(' '), ord(' '))     # error code ("  " is a normal return)
        # Note that _f5090 will *not* reset the flag upon success so it must be initialized to "  "

        # Call the appropriate function in the f-curves library
        if curve_enum in [PropagationCurve.curve_50_50, PropagationCurve.curve_50_10]:
            self._tvfmfs_metric(byref(erp), byref(haat), byref(channel), byref(field_strength_dbu), byref(distance),
                        byref(switch), byref(curve), byref(flag), 2)
        elif curve_enum in [PropagationCurve.curve_50_90, ]:
            self._f5090(byref(erp), byref(haat), byref(channel), byref(field_strength_dbu), byref(distance),
                        byref(switch), byref(flag), 2)
        else:
            raise ValueError("No curve associated with %d. Please see the PropagationCurve class for options." % curve_enum)

        # Check for warnings from the library
        self._raise_warning_or_error_if_flag_set(flag)

        # Since our input value was 1 Watt, this will actually be the pathloss coefficient
        return self.dBu_to_Watts(field_strength_dbu.value, frequency)

    def get_distance_unchecked(self, pathloss_coefficient, frequency=None, tx_height=None, rx_height=None,
                               tx_location=None, rx_location=None, curve_enum=None):
        erp = c_float(1e-3)     # 1 W (.001 kW)     DO NOT CHANGE
        haat = c_float(self._get_haat(tx_height, tx_location, rx_location))   # meters

        # Since the input ERP is 1 W, we can use the pathloss coefficient directly
        pathloss_dBu = self.Watts_to_dBu(pathloss_coefficient, frequency)
        field_strength_dbu = c_float(pathloss_dBu)
        channel = c_long(self._get_proxy_channel_number(frequency))
        curve = c_long(self._get_curve_integer(curve_enum))
        switch = c_long(2)      # 1 = compute field strength from distance
                                # 2 = compute distance from field strength

        distance = c_float(100)        # km    # this will hold the output
        flag = (c_byte*2)(ord(' '), ord(' '))     # error code ("  " is a normal return)
        # Note that _f5090 will *not* reset the flag upon success so it must be initialized to "  "

        # Call the appropriate function in the f-curves library
        if curve_enum in [PropagationCurve.curve_50_50, PropagationCurve.curve_50_10]:
            self._tvfmfs_metric(byref(erp), byref(haat), byref(channel), byref(field_strength_dbu), byref(distance),
                                byref(switch), byref(curve), byref(flag), 2)
        elif curve_enum in [PropagationCurve.curve_50_90, ]:
            self._f5090(byref(erp), byref(haat), byref(channel), byref(field_strength_dbu), byref(distance),
                        byref(switch), byref(flag), 2)
        else:
            raise ValueError("No curve associated with %d. Please see the PropagationCurve class for options." \
                             % curve_enum)

        # Check for warnings from the library
        self._raise_warning_or_error_if_flag_set(flag)

        return distance.value


    def _get_haat(self, reported_haat, tx_location, rx_location):
        # TODO: update this function to use terrain
        return reported_haat

####
#   DESCRIPTIVE PROPERTIES
####
    def requires_terrain(self):
        return True

    def requires_tx_height(self):
        return False

    def requires_rx_height(self):
        return False

    def requires_frequency(self):
        return True

    def requires_tx_location(self):
        return True

    def requires_rx_location(self):
        return True

    def requires_curve_enum(self):
        return True
####
#   END DESCRIPTIVE PROPERTIES
####





class PropagationModelFcurvesWithoutTerrain(PropagationModelFcurves):
    """
    Identical to :meth:`PropagationModelFcurves` except the transmitter and receiver locations are not required (i.e.
    the provided transmitter HAAT is used without modification).
    """
    def requires_terrain(self):
        return False

    def requires_tx_height(self):
        return True

    def requires_tx_location(self):
        return False

    def requires_rx_location(self):
        return False

    def get_haat(self, reported_haat, tx_location, rx_location):
        if not self.requires_terrain():
            return reported_haat

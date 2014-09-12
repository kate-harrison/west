from protected_entity import ProtectedEntity
import helpers

class ProtectedEntityTVStation(ProtectedEntity):
    """TV station"""

    required_properties = ["_latitude", "_longitude", "_channel", "_ERP_Watts", "_HAAT_meters", "_tx_type"]

    def __init__(self, container, region, latitude, longitude, channel, ERP_Watts, HAAT_meters, tx_type):
        super(ProtectedEntityTVStation, self).__init__(region, container, latitude, longitude)

        self._channel = channel
        self._ERP_Watts = ERP_Watts
        self._HAAT_meters = HAAT_meters
        self._tx_type = tx_type

        # TODO: bring this back
        if not (self.is_digital() ^ self.is_analog()):
           self.log.error("Transmitter type not recognized as analog or "
                          "digital: '%s'. Please edit the configuration to "
                          "add this type.", self.get_tx_type())

        # Optional information that can be added later
        self._facility_id = None
        self._callsign = None

        self._log_error_if_necessary_data_missing()

    def to_string(self):
        """
        Returns some of the TV station's information as a formatted string.
        """
        output = ""
        output += "Location: (%f,%f)" % (self._latitude, self._longitude) + "\n"
        output += "Type: %s" % self._tx_type + "\t"
        output += "Channel: %d" % self._channel + "\t"
        output += "ERP (kW): %.2f" % (self._ERP_Watts/1000) + "\t"
        output += "HAAT (m): %f" % self._HAAT_meters + "\n"
        output += "Callsign: %s" % str(self._callsign) + "\n"

        return output

    def add_facility_id(self, facility_id):
        """
        Add the facility ID associated with the TV station.
        """
        self._facility_id = facility_id

    def get_facility_id(self):
        """
        Returns a string containing the facility ID associated with the TV station (if any) or None.
        """
        return self._facility_id

    def add_callsign(self, callsign):
        """
        Add the callsign associated with the TV station.
        """
        self._callsign = callsign

    def get_callsign(self):
        """
        Returns a string containing the callsign associated with the TV station (if any) or None.
        """

    def get_location(self):
        return (self._latitude, self._longitude)

    def get_channel(self):
        return self._channel

    def get_erp_watts(self):
        """
        Returns the ERP (effective radiated power) of the TV station in Watts.
        """
        return self._ERP_Watts

    def get_erp_kilowatts(self):
        """
        Returns the ERP (effective radiated power) of the TV station in kilowatts.
        """
        return self._ERP_Watts / 1000.0

    def get_haat_meters(self):
        """
        Returns the HAAT (height above average terrain) of the TV station in meters.
        """
        return self._HAAT_meters

    def get_tx_type(self):
        """
        Returns the transmitter type of the TV station (depends on source data). If possible, use :meth:`is_digital`
        and :meth:`is_analog` to avoid dependence on source data.
        """
        return self._tx_type

    def is_digital(self):
        """
        Returns True if the TV station is digital and False otherwise. See also :meth:`is_analog`.
        """
        return self._tx_type in self.container.digital_tv_types()

    def is_analog(self):
        """
        Returns True if the TV station is analog and False otherwise. See also :meth:`is_digital`.
        """
        return self._tx_type in self.container.analog_tv_types()

    def is_cochannel(self, channel):
        """
        Returns True if `channel` is the same as this station's channel and False otherwise.
        """
        return self._channel == channel

    def is_adjacent_channel(self, channel):
        """
        Returns True if `channel` is adjacent to this station's channel and False otherwise. See also
        :meth:`helpers.channels_are_adjacent_in_frequency`.
        """
        return helpers.channels_are_adjacent_in_frequency(self.container.get_mutable_region(), self._channel, channel)

    def add_to_kml(self, kml):
        point = kml.newpoint()
        point.name = str(self._callsign)
        point.description = """
        Channel: %d
        Transmitter type: %s
        ERP: %.2f kW
        HAAT: %.2f meters
        Latitude: %.2f
        Longitude: %.2f
        Callsign: %s
        Facility ID: %s
        """ % (self.get_channel(), self.get_tx_type(), self.get_erp_kilowatts(), self.get_haat_meters(),
               self.get_latitude(), self.get_longitude(), self.get_callsign(), self.get_facility_id())
        point.coords = [(self.get_longitude(), self.get_latitude())]
        return point

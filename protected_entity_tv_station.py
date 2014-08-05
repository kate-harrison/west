from protected_entity import ProtectedEntity
from protected_entities import ProtectedEntities
import helpers
from geopy.distance import VincentyDistance
from geopy import Point
# from doc_inherit import doc_inherit

class ProtectedEntityTVStation(ProtectedEntity):
    """TV station"""

    def __init__(self, container, region, latitude, longitude, channel, ERP_Watts, HAAT_meters, tx_type):
        super(ProtectedEntityTVStation, self).__init__(region)

        self.container = container
        if not isinstance(container, ProtectedEntities):
            # TODO: raise an exception?
            self.log.error("Container is not a ProtectedEntities instance: got %s instead." % container.__class__.__name__)
        self.latitude = latitude
        self.longitude = longitude
        self.channel = channel
        self.ERP_Watts = ERP_Watts
        self.HAAT_meters = HAAT_meters
        self.tx_type = tx_type

        # TODO: bring this back
        if not (self.is_digital() ^ self.is_analog()):
           self.log.error("Transmitter type not recognized as analog or "
                          "digital: '%s'. Please edit the configuration to "
                          "add this type.", self.tx_type)

        # Optional information that can be added later
        self.facility_id = None
        self.callsign = None

        self._create_bounding_box()

        self.log_error_if_necessary_data_missing()

    def to_string(self):
        output = ""
        output += "Location: (%f,%f)" % (self.latitude, self.longitude) + "\n"
        output += "Type: %s" % self.tx_type + "\t"
        output += "Channel: %d" % self.channel + "\t"
        output += "ERP (kW): %.2f" % (self.ERP_Watts/1000) + "\t"
        output += "HAAT (m): %f" % self.HAAT_meters + "\n"

        return output

    def add_facility_id(self, facility_id):
        self.facility_id = facility_id

    def add_callsign(self, callsign):
        self.callsign = callsign

    def get_location(self):
        return (self.latitude, self.longitude)

    def get_channel(self):
        return self.channel

    def get_erp_watts(self):
        return self.ERP_Watts

    def get_erp_kilowatts(self):
        return self.ERP_Watts / 1000.0

    def get_haat_meters(self):
        return self.HAAT_meters

    def get_tx_type(self):
        return self.tx_type

    def is_digital(self):
        return self.tx_type in self.container.digital_tv_types()

    def is_analog(self):
        return self.tx_type in self.container.analog_tv_types()

    def is_cochannel(self, channel):
        return self.channel == channel

    def is_adjacent_channel(self, channel):
        return helpers.channels_are_adjacent_in_frequency(self.container.simulation.get_mutable_region(), self.channel, channel)

    def add_to_kml(self, kml):
        point = kml.newpoint()
        point.name = str(self.callsign)
        point.description = """
        Channel: %d
        Transmitter type: %s
        ERP: %.2f kW
        HAAT: %.2f meters
        Latitude: %.2f
        Longitude: %.2f
        """ % (self.get_channel(), self.get_tx_type(), self.get_erp_kilowatts(), self.get_haat_meters(),
               self.get_latitude(), self.get_longitude())
        point.coords = [(self.get_longitude(), self.get_latitude())]
        return point

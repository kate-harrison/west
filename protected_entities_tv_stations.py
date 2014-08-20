from abc import abstractmethod
from protected_entities import ProtectedEntities
from protected_entity_tv_station import ProtectedEntityTVStation
import os
import helpers
import csv
import configuration


class ProtectedEntitiesTVStations(ProtectedEntities):
    """This class contains multiple TV stations."""

    def __init__(self, *args, **kwargs):
        super(ProtectedEntitiesTVStations, self).__init__(*args, **kwargs)
        self._categorize_stations()

    @abstractmethod
    def digital_tv_types(self):
        """Returns a list of the TV station types corresponding to digital
        TV."""
        return

    @abstractmethod
    def analog_tv_types(self):
        """Returns a list of the TV station types corresponding to analog TV."""
        return

    @abstractmethod
    def ignored_tv_types(self):
        """Returns a list of TV station types which will be ignored."""
        return

    def get_list_of_entities_on_channel(self, channel):
        return self.stations_by_channel[channel]


    def stations(self):
        return self._entities

    def _categorize_stations(self):
        """Put the stations into a few dictionaries for easy access."""
        self.log.debug("Categorizing TV stations")
        self.stations_by_tx_type = {}
        self.stations_by_channel = {}
        self.stations_by_DA = {'analog': [], 'digital': []}

        for station in self.stations():
            channel = station.get_channel()
            tx_type = station.get_tx_type()
            is_digital = station.is_digital()

            if channel not in self.stations_by_channel:
                self.stations_by_channel[channel] = []
            self.stations_by_channel[channel].append(station)

            if tx_type not in self.stations_by_tx_type:
                self.stations_by_tx_type[tx_type] = []
            self.stations_by_tx_type[tx_type].append(station)

            if is_digital:
                self.stations_by_DA['digital'].append(station)
            else:
                self.stations_by_DA['analog'].append(station)

    def print_station_statistics(self):
        """Prints aggregate statistics about the stations."""

        print(helpers.horizontal_separator)

        # Number of stations on each channel
        for (k, v) in self.stations_by_channel.iteritems():
            print("Channel %d: %d towers" % (k, len(v)))

        print(helpers.horizontal_separator)

        for (k, v) in self.stations_by_tx_type.iteritems():
            print("There are %d towers of type %s" % (len(v), k))

        print(helpers.horizontal_separator)

        num_towers = 0
        for (k, v) in self.stations_by_DA.iteritems():
            num_towers = num_towers + len(v)
            print("There are %d %s towers" % (len(v), k))

        print(helpers.horizontal_separator)

        print("There are %d total towers" % num_towers)
        print(helpers.horizontal_separator)



class ProtectedEntitiesTVStationsUnitedStates(ProtectedEntitiesTVStations):
    """Defines some of the common properties of US TV stations."""

    # FYI: cannot use doc_inherit in this class without running into a max recursion depth limit (TODO: look into this)

    def digital_tv_types(self):
        return ['DT', 'DC', 'LD', 'DS', 'DX']

    def analog_tv_types(self):
        return ['CA', 'TX', 'TS']

    def ignored_tv_types(self):
        return ['DD']

    def get_max_protected_radius_km(self):
        """
        See :meth:`protected_entities.ProtectedEntities.get_max_protected_radius_km` for more details.

        :return: 200.0
        :rtype: float
        """
        return 200.0


class ProtectedEntitiesTVStationsUnitedStatesFromGoogle(ProtectedEntitiesTVStationsUnitedStates):
    """This class contains TV stations as read from the Google data."""

    def source_filename(self):
        base_directory = configuration.paths['UnitedStates']['protected_entities']
        return os.path.join(base_directory, 'FromGoogle', 'tv_us.csv')

    def source_name(self):
        return "Google TVWS database download [" \
               "http://www.google.com/get/spectrumdatabase/data/]"

    def _load_entities(self):
        """Example entry from Google's data:

        {'rcamsl_meters': '1348.1', 'application_id': '1297384', 'uid': 'KHMT',
        'erp_watts': '1000000.000', 'site_number': '0', 'parent_latitude': '',
        'entity_type': 'TV_US', 'keyhole_radius_meters': '',
        'antenna_rotation_degrees': '0.0', 'latitude': '45.739956',
        'tx_type': 'DT', 'channel': '22', 'parent_longitude': '',
        'facility_id': '47670', 'circle_radius_meters': '',
        'location_type': 'POINT', 'data_source': 'CDBS', 'rcagl_meters': '112.1',
        'geometry': '', 'longitude': '-108.139013', 'haat_meters': '247.5',
        'azimuth': '', 'antenna_id': '77895', 'parent_facility_id': '',
        'parent_callsign': ''}
        """

        self.log.debug("Loading TV stations from \"%s\" (%s)" % (str(self.source_filename()), str(self.source_name())))

        with open(self.source_filename(), 'r') as f:
            station_csv = csv.DictReader(f)
            for station in station_csv:

                tx_type = station['tx_type']

                # Skip distributed digital stations
                if tx_type in self.ignored_tv_types():
                    continue

                try:
                    latitude = float(station['latitude'])
                    longitude = float(station['longitude'])
                    channel = int(station['channel'])
                    ERP = float(station['erp_watts'])
                    haat = float(station['haat_meters'])
                except Exception as e:
                    self.log.error("Error loading station: ", str(e))
                    continue

                new_station = ProtectedEntityTVStation(self, self.get_mutable_region(), latitude=latitude,
                                                       longitude=longitude, channel=channel, ERP_Watts=ERP,
                                                       HAAT_meters=haat, tx_type=tx_type)

                # Add optional information
                new_station.add_facility_id(station['facility_id'])
                new_station.add_callsign(station['uid'])

                self._add_entity(new_station)

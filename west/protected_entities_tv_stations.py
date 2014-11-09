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
        self._refresh_cached_data()

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

    def get_list_of_entities_on_channel(self, channel_number):
        if channel_number not in self.region.get_channel_list():
            raise ValueError("Unsupported channel number: %d" % channel_number)
        return self.stations_by_channel[channel_number]


    def stations(self):
        return self._entities

    def _refresh_cached_data(self):
        """Put the stations into a few dictionaries for easy access."""
        self.log.debug("Categorizing TV stations")
        self.stations_by_tx_type = {}
        self.stations_by_channel = {}
        self.stations_by_DA = {'analog': [], 'digital': []}

        # Pre-allocate the channels so that an empty list is returned even if
        # there are no stations on that channel. Stations which have a
        # channel not in the list will not be added.
        for channel_number in self.region.get_channel_list():
            self.stations_by_channel[channel_number] = []

        for station in self.stations():
            channel = station.get_channel()
            tx_type = station.get_tx_type()
            is_digital = station.is_digital()

            if channel not in self.stations_by_channel:
                self.log.warning("Detected a station on an unsupported "
                                 "channel: %d" % channel)
            else:
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

    def digital_tv_types(self):
        return ['DT', 'DC', 'LD', 'DS', 'DX']

    def analog_tv_types(self):
        return ['CA', 'TX', 'TS', 'TV']

    def ignored_tv_types(self):
        return ['DD', 'LM']     # distributed digital, land mobile

    def get_max_protected_radius_km(self):
        """
        See
        :meth:`protected_entities.ProtectedEntities.get_max_protected_radius_km`
        for more details.

        :return: 200.0
        :rtype: float
        """
        return 200.0


class ProtectedEntitiesTVStationsUnitedStatesIncentiveAuctionBaseline2014May20(
    ProtectedEntitiesTVStationsUnitedStates):
    """This class contains TV stations read from the FCC's Baseline file for
    the incentive auctions. The file can be found at
    http://data.fcc.gov/download/incentive-auctions/Constraint_Files/
    (specifically at
    http://data.fcc.gov/download/incentive-auctions/Constraint_Files/US_Station_Baseline_2014May20.xlsx
    ).
    """
    def source_filename(self):
        base_directory = configuration.paths['UnitedStates']['protected_entities']
        return os.path.join(base_directory,
                            'us_station_baseline_2014may20 - US Stations.csv')

    def source_name(self):
        return "US Station Incentive Auction Baseline May 20, 2014 " + \
               "[http://data.fcc.gov/download/incentive-auctions/Constraint_Files/]"

    def _load_entities(self):
        """
        Column headers + example data (copied from spreadsheet). More
        information about the columns is available in the original .xlsx file.

        channel	service	country	state	city	lat	lon	fac_callsign	arn	app_id	haat	da	erp	facility_id	rcamsl	ref az	ant_id
        5	DT	US	AK	ANCHORAGE	612011	1493047	KYES-TV	BLCDT20110307ACV	1565982	277	DA	15	21488	614.5	0	93311
        """
        self.log.debug("Loading TV stations from \"%s\" (%s)" % (str(
            self.source_filename()), str(self.source_name())))

        def convert_dms_to_decimal(degrees, minutes, seconds):
            return degrees + minutes/60 + seconds/3600

        with open(self.source_filename(), 'r') as f:
            station_csv = csv.DictReader(f)
            for station in station_csv:
                tx_type = station['service']

                if tx_type in self.ignored_tv_types():
                    self.log.debug("Skipping TV station because its type is "
                                   "ignored: %s" % tx_type)
                    continue

                try:
                    # Lat/lon are in format DDDMMSS
                    lat_string = station['lat']
                    lat_sec = float(lat_string[-2:])
                    lat_min = float(lat_string[-4:-2])
                    lat_deg = float(lat_string[:-4])
                    latitude = convert_dms_to_decimal(lat_deg, lat_min, lat_sec)

                    lon_string = station['lon']
                    lon_sec = float(lon_string[-2:])
                    lon_min = float(lon_string[-4:-2])
                    lon_deg = float(lon_string[:-4])
                    longitude = convert_dms_to_decimal(lon_deg, lon_min,
                                                       lon_sec) * -1

                    channel = int(station['channel'])
                    ERP_kW = float(station['erp'])  # in kW
                    haat = float(station['haat'])  # in meters
                except Exception as e:
                    self.log.error("Error loading station: ", str(e))
                    continue

                new_station = ProtectedEntityTVStation(self,
                                                       self.get_mutable_region(),
                                                       latitude=latitude,
                                                       longitude=longitude,
                                                       channel=channel,
                                                       ERP_Watts=ERP_kW*1e3,
                                                       HAAT_meters=haat,
                                                       tx_type=tx_type)

                # Add optional information
                new_station.add_facility_id(station['facility_id'])
                new_station.add_callsign(station['fac_callsign'])
                new_station.add_app_id(station['app_id'])

                self._add_entity(new_station)


class ProtectedEntitiesTVStationsUnitedStatesTVQuery(
    ProtectedEntitiesTVStationsUnitedStates):
    """This class contains TV stations as read from the TV Query website.
    Subclasses will contain data from a particular date.

    TVQuery: http://www.fcc.gov/encyclopedia/tv-query-broadcast-station-search
    Key: http://transition.fcc.gov/mb/audio/am_fm_tv_textlist_key.txt
    """

    def _load_entities(self):
        """Example entry:

        ['', 'K02JU       ', '-         ', 'TX ', '2   ', 'DA  ', '                    ', '-  ', '-  ', 'LIC    ',
        'SELAWIK                  ', 'AK ', 'US ', 'BLTTV  -19800620IA  ', '0.018  kW ', '-         ', '0.0     ',
        '-       ', '11543      ', 'N ', '66 ', '35 ', '57.00 ', 'W ', '160 ', '0  ', '0.00  ',
        'CITY OF SELAWIK                                                             ', '   0.00 km ', '   0.00 mi ',
        '  0.00 deg ', '72.    m', 'H       ', '20773     ', '210.    ', '-       ', '0.      ', '21309     ', '-  ',
        '']

        Key: http://transition.fcc.gov/mb/audio/am_fm_tv_textlist_key.txt
        """
        self.log.debug("Loading TV stations from \"%s\" (%s)" % (str(
            self.source_filename()), str(self.source_name())))

        column_number = dict()
        column_number['callsign'] = 1
        column_number['tx_type'] = 3
        column_number['channel'] = 4
        column_number['country'] = 12
        column_number['ERP_kW'] = 14
        column_number['HAAT'] = 16
        column_number['facility_id'] = 18
        column_number['lat_dir'] = 19
        column_number['lat_deg'] = 20
        column_number['lat_min'] = 21
        column_number['lat_sec'] = 22
        column_number['lon_dir'] = 23
        column_number['lon_deg'] = 24
        column_number['lon_min'] = 25
        column_number['lon_sec'] = 26
        column_number['km_offset'] = 28
        column_number['app_id'] = -3

        def convert_dms_to_decimal(degrees, minutes, seconds):
            return degrees + minutes/60 + seconds/3600

        with open(self.source_filename(), 'r') as f:
            station_csv = csv.reader(f, delimiter='|')

            for station_row in station_csv:
                # Skip blank rows
                if len(station_row) == 0:
                    continue

                try:
                    callsign = station_row[column_number['callsign']].strip()

                    # Skip "vacant" entries
                    if callsign in ['VACANT']:
                        continue

                    # Skip stations which are not in the US
                    if str.strip(station_row[column_number['country']]) in [
                        "CA", "MX"]:
                        continue

                    tx_type = str.strip(station_row[column_number['tx_type']])

                    # The second list holds types which designate petitions
                    if tx_type in self.ignored_tv_types() or tx_type in [
                        'DM', 'DR', 'DN']:
                        continue

                    channel = int(station_row[column_number['channel']])
                    # Skip stations that are outside the channel bounds
                    # See Q&A from 7/13/11 at
                    # http://www.fcc.gov/encyclopedia/white-space-database-administration-q-page:
                    #   "Database systems are not required to provide adjacent channel protection to legacy services
                    #    from the TV bands that are continuing to operate on channel 52."
                    if channel > 51:
                        continue

                    ERP_kW_string = station_row[column_number['ERP_kW']].split(" ")[0]
                    ERP_Watts = float(ERP_kW_string) * 1e3
                    # Skip stations with an ERP that is zero
                    # The FCC whitespace database administrators FAQ page
                    # (http://www.fcc.gov/encyclopedia/white-space-database-administration-q-page) mentions visual peak
                    # power and visual average power; however, these values are not present in the TV Query data.
                    if ERP_Watts < 0.001:
                        self.log.warning("Skipping station with 0 kW ERP; "
                                         "callsign: '%s'" % callsign)
                        continue

                    # Convert latitude
                    lat_dir = str.strip(station_row[column_number['lat_dir']])
                    lat_deg = float(station_row[column_number['lat_deg']])
                    lat_min = float(station_row[column_number['lat_min']])
                    lat_sec = float(station_row[column_number['lat_sec']])
                    if lat_dir in ['n', 'N']:
                        lat_sign = 1
                    elif lat_dir in ['s', 'S']:
                        lat_sign = -1
                    else:
                        self.log.error("Could not determine station latitude "
                                       "(direction: %s); skipping station "
                                       "with callsign %s" %
                                       (lat_dir, callsign))
                        print station_row
                        continue
                    latitude = lat_sign * convert_dms_to_decimal(lat_deg,
                                                                 lat_min,
                                                                 lat_sec)

                    # Convert longitude
                    lon_dir = str.strip(station_row[column_number['lon_dir']])
                    lon_deg = float(station_row[column_number['lon_deg']])
                    lon_min = float(station_row[column_number['lon_min']])
                    lon_sec = float(station_row[column_number['lon_sec']])
                    if lon_dir in ['e', 'E']:
                        lon_sign = 1
                    elif lon_dir in ['w', 'W']:
                        lon_sign = -1
                    else:
                        self.log.error(
                            "Could not determine station longitude ("
                            "direction: %s); skipping station with callsign "
                            "%s" % (
                            lon_dir, callsign))
                        print station_row
                        continue
                    longitude = lon_sign * convert_dms_to_decimal(lon_deg,
                                                                  lon_min,
                                                                  lon_sec)

                    HAAT_meters = float(station_row[column_number['HAAT']])
                except Exception as e:
                    self.log.error("Error loading station: ", str(e))
                    continue

                # Create the station
                new_station = ProtectedEntityTVStation(self,
                                                       self.get_mutable_region(),
                                                       latitude=latitude,
                                                       longitude=longitude,
                                                       channel=channel,
                                                       ERP_Watts=ERP_Watts,
                                                       HAAT_meters=HAAT_meters,
                                                       tx_type=tx_type)

                # Add optional information
                new_station.add_facility_id(
                    station_row[column_number['facility_id']].strip())
                new_station.add_callsign(callsign)

                new_station.add_app_id(
                    station_row[column_number['app_id']].strip())

                # Add it to the internal list
                self._add_entity(new_station)


class ProtectedEntitiesTVStationsUnitedStatesTVQuery2014June17(
    ProtectedEntitiesTVStationsUnitedStatesTVQuery):
    """TV Query data from June 17, 2014."""

    def source_filename(self):
        base_directory = \
            configuration.paths['UnitedStates']['protected_entities']
        return os.path.join(base_directory, '2014-06-17 tvq.txt')

    def source_name(self):
        return "TVQuery download on June 17, 2014 " + \
                "[http://www.fcc.gov/encyclopedia/tv-query-broadcast-station-search]"


class ProtectedEntitiesTVStationsUnitedStatesFromGoogle(
    ProtectedEntitiesTVStationsUnitedStates):
    """This class contains TV stations as read from the Google data."""

    def source_filename(self):
        base_directory = \
            configuration.paths['UnitedStates']['protected_entities']
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

        self.log.debug("Loading TV stations from \"%s\" (%s)" % (
        str(self.source_filename()), str(self.source_name())))

        with open(self.source_filename(), 'r') as f:
            station_csv = csv.DictReader(f)
            for station in station_csv:

                tx_type = station['tx_type']

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

                new_station = ProtectedEntityTVStation(self,
                                                       self.get_mutable_region(),
                                                       latitude=latitude,
                                                       longitude=longitude,
                                                       channel=channel,
                                                       ERP_Watts=ERP,
                                                       HAAT_meters=haat,
                                                       tx_type=tx_type)

                # Add optional information
                new_station.add_facility_id(station['facility_id'])
                new_station.add_callsign(station['uid'])
                new_station.add_app_id(station['application_id'])

                self._add_entity(new_station)

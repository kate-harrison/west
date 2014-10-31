import data_map
from abc import ABCMeta, abstractmethod
from custom_logging import getModuleLogger
import configuration
import os
import csv
import shapely
from shapely.geometry import shape
import fiona


class PopulationNugget(object):
    """
    Holds a single population-geometry/geography pair. This class provides a
    standardized data format for use with
    :meth:`PopulationData.create_population_map`.
    """

    def __init__(self, identifier):
        self._geometry = None
        self._population = None
        self._identifier = identifier

    def add_geometry(self, geometry):
        self._geometry = geometry

    def get_geometry(self):
        return self._geometry

    def is_valid(self):
        return self._geometry is not None and self._population is not None

    def get_population(self):
        return self._population

    def add_population(self, population):
        self._population = float(population)

    def to_string(self):
        return "Has geometry: %s\nPopulation: %s" % (str(self._geometry is
                                                         not None),
                                                     str(self._population))


class PopulationData(object):
    """
    This class defines the interface for all Population classes. A Population
    object is defined by its data source. This data source is transformed into
    :class:`PopulationNugget` objects, which are later used to compute a
    :class:`data_map.DataMap2D` where each pixel's value represents the
    population inside that pixel.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        self.log = getModuleLogger(self)
        self._population_nuggets_by_identifier = {}
        self._load_populations()
        self._load_geography()
        self._prune_invalid_population_nuggets()

    def _prune_invalid_population_nuggets(self):
        num_nuggets_before_pruning = len(
            self._population_nuggets_by_identifier.keys())
        self._population_nuggets_by_identifier = \
            {identifier: nugget
             for identifier, nugget in
             self._population_nuggets_by_identifier.items()
             if nugget.is_valid()}
        num_nuggets_after_pruning = len(
            self._population_nuggets_by_identifier.keys())

        if num_nuggets_after_pruning == num_nuggets_before_pruning:
            self.log.debug("No population nuggets were pruned.")
        else:
            self.log.debug(
                "%d population nuggets were pruned due to insufficient data "
                "(%d remaining)" %
                (num_nuggets_before_pruning - num_nuggets_after_pruning,
                 num_nuggets_after_pruning))

    @abstractmethod
    def data_year(self):
        """int describing the year of the data."""
        return

    @abstractmethod
    def geography_source_filenames(self):
        """List of filenames for the geographical source data."""
        return

    @abstractmethod
    def population_source_filenames(self):
        """List of filenames for the population source data."""
        return

    @abstractmethod
    def geography_source_name(self):
        """String version of the geographical source data."""
        return

    @abstractmethod
    def population_source_name(self):
        """String version of the population source data."""
        return

    @abstractmethod
    def resolution_description(self):
        """String describing the geographic resolution of the data."""
        pass

    @abstractmethod
    def _load_geography(self):
        pass

    @abstractmethod
    def _load_populations(self):
        pass

    def create_population_map(self, is_in_region_datamap2d):
        """
        Creates a new :class:`data_map.DataMap2D` whose values represent the
        population contained in the respective pixel. The shape of the
        DataMap2D will be taken from the input DataMap2D. Furthermore,
        pixels whose value in the input DataMap2D is False will be skipped in
        the population computation.
        """
        # Note: will use is_in_region map to help but will not modify it
        population_datamap2d = data_map.DataMap2D.get_copy_of(
            is_in_region_datamap2d)
        population_datamap2d.reset_all_values(
            0)  # set everything to 0 so we can accumulate

        latitude_width_degrees = self._calculate_latitude_width_degrees(
            is_in_region_datamap2d.latitudes)
        longitude_width_degrees = self._calculate_longitude_width_degrees(
            is_in_region_datamap2d.longitudes)

        def calculate_population(latitude, longitude, latitude_index,
                                 longitude_index, current_value):
            if not is_in_region_datamap2d.get_value_by_index(latitude_index,
                                                             longitude_index):
                return None

            return self._calculate_population_for_pixel((latitude, longitude),
                                                        latitude_width_degrees,
                                                        longitude_width_degrees)

        population_datamap2d.update_all_values_via_function(
            calculate_population, verbose=True)

        return population_datamap2d

    def _calculate_population_for_pixel(self, location, latitude_width_degrees,
                                        longitude_width_degrees):
        current_pop = 0
        pixel_polygon = self._create_pixel_polygon(location,
                                                   latitude_width_degrees,
                                                   longitude_width_degrees)
        for population_nugget in self._population_nuggets_by_identifier.values():
            current_pop += self._get_population_contribution(pixel_polygon,
                                                             population_nugget)
        return current_pop

    def _get_population_contribution(self, pixel_polygon, population_nugget):
        if not pixel_polygon.intersects(population_nugget.get_geometry()):
            return 0

        intersection = pixel_polygon.intersection(
            population_nugget.get_geometry())
        intersection_area = intersection.area
        nugget_area = population_nugget.get_geometry().area

        # Note: shapely does not know that these are geo coordinates; the
        # area here is an approximation
        fraction_of_area_in_this_pixel = intersection_area / nugget_area

        return population_nugget.get_population() * fraction_of_area_in_this_pixel

    def _calculate_latitude_width_degrees(self, latitude_list):
        # Assumes even spacing
        return latitude_list[1] - latitude_list[0]

    def _calculate_longitude_width_degrees(self, longitude_list):
        # Assumes even spacing
        return longitude_list[1] - longitude_list[0]

    def _create_pixel_polygon(self, location, latitude_width_degrees,
                              longitude_width_degrees):
        latitude, longitude = location
        min_lat = latitude - latitude_width_degrees / 2.0
        max_lat = latitude + latitude_width_degrees / 2.0
        min_lon = longitude - longitude_width_degrees / 2.0
        max_lon = longitude + longitude_width_degrees / 2.0

        exterior = [(min_lon, max_lat), (max_lon, max_lat), (max_lon, min_lat),
                    (min_lon, min_lat)]
        return shapely.geometry.Polygon(exterior)


class ShapefilePopulationData(PopulationData):
    """ Provide some methods that make population data generation easier with
    shapefiles.
    """

    def _read_shapefile(self, filename):
        """
        Read the shapefile specified by :meth:`boundary_filename`. Provides
        support for multi-part polygons.
        """
        geometries_and_properties = []

        with fiona.open(filename, "r") as source:
            for f in source:
                try:
                    geom = shape(f['geometry'])
                    if not geom.is_valid:
                        clean = geom.buffer(0.0)
                        assert clean.is_valid
                        assert clean.geom_type == 'Polygon'
                        geom = clean
                    geometries_and_properties.append((geom, f['properties']))
                except Exception as e:
                    self.log.error(
                        "Error reading in %s: %s" % (filename, str(e)))

        return geometries_and_properties


class PopulationDataUnitedStates2010(ShapefilePopulationData):
    """
    Population data for the United States based on the 2010 census.

    Note: computation for a 200x300 DataMap2D may take several hours.
    """

    def data_year(self):
        return 2010

    def _fips_code_list(self):
        # Reference: http://en.wikipedia.org/wiki/FIPS_state_code
        fips_code_list = range(1, 57)
        fips_code_list.remove(3)  # American Samoa
        fips_code_list.remove(7)  # Canal Zone
        fips_code_list.remove(14)  # Guam
        fips_code_list.remove(43)  # Puerto Rico
        fips_code_list.remove(52)  # US Virgin Islands
        return fips_code_list

    def geography_source_filenames(self):
        base_directory = os.path.join(
            configuration.paths['UnitedStates']['population'],
            str(self.data_year()))
        filename_list = []
        for fips_code in self._fips_code_list():
            base_filename = "gz_2010_%02d_140_00_500k" % fips_code
            # For example,
            # Population/2010/gz_2010_01_140_00_500k/gz_2010_01_140_00_500k.shp
            filename_list.append(os.path.join(base_directory, base_filename,
                                              base_filename + ".shp"))

        return filename_list

    def population_source_filenames(self):
        return [os.path.join(configuration.paths['UnitedStates']['population'],
                             str(self.data_year()),
                             "popbytract2010.csv"), ]

    def geography_source_name(self):
        return "US census bureau (http://www2.census.gov/geo/tiger/GENZ2010/" \
               + " or " + \
               "https://www.census.gov/geo/maps-data/data/cbf/cbf_tracts.html)"

    def population_source_name(self):
        return "US census bureau"

    def resolution_description(self):
        return "Census tract"

    def _load_geography(self):
        geometries_and_properties = []
        for filename in self.geography_source_filenames():
            geometries_and_properties += self._read_shapefile(filename)

        for (geometry, properties) in geometries_and_properties:
            # Sample properties:
            # OrderedDict([(u'GEO_ID', u'1400000US01051031000'), (u'STATE', u'01'), (u'COUNTY', u'051'),
            # (u'TRACT', u'031000'), (u'NAME', u'310'), (u'LSAD', u'Tract'), (u'CENSUSAREA', 9.083)])

            # Example GEOID: 1400000US01051031000
            # Corresponding identifier: 01051031000
            identifier = properties['GEO_ID'][9:]
            if identifier not in self._population_nuggets_by_identifier:
                self._population_nuggets_by_identifier[
                    identifier] = PopulationNugget(identifier)

            self._population_nuggets_by_identifier[identifier].add_geometry(
                geometry)

    def _load_populations(self):
        population_filename = self.population_source_filenames()[0]
        with open(population_filename, "r") as f:
            population_csv = csv.DictReader(f)

            for row in population_csv:
                identifier = row['GEOID']
                population = row['POP100']

                if identifier not in self._population_nuggets_by_identifier:
                    self._population_nuggets_by_identifier[
                        identifier] = PopulationNugget(identifier)

                self._population_nuggets_by_identifier[
                    identifier].add_population(population)

from abc import ABCMeta, abstractmethod
from os import path
from custom_logging import getModuleLogger
from shapely.geometry import Point, shape
import shapely
import fiona
import configuration

class Boundary(object):
    """
    Defines the boundary of a particular region (e.g. states in the United States). Contains one or more
    :class:`shapely.geometry.Polygon` objects.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.log = getModuleLogger(self)

        self._geometries = []

    @abstractmethod
    def boundary_filename(self):
        """
        :return: name of the boundary file (e.g. boundary.shp)
        :rtype: string
        """
        return

    def location_inside_boundary(self, location):
        """
        Tests whether or not the location is included in this boundary.

        :param location: (latitude, longitude)
        :type location: pair of floats
        :return: True if the location is inside the boundary and False otherwise
        :rtype: boolean
        """

        return self.point_inside_boundary(Point( (location[1], location[0]) ))

    def point_inside_boundary(self, point):
        """
        Tests whether or not the point is included in this boundary.

        :param point:
        :type point: :class:`shapely.geometry.Point`
        :return: True if the location is inside the boundary and False otherwise
        :rtype: boolean
        """
        for geometry in self._geometries:
            if point.within(geometry):
                return True

        return False

    @abstractmethod
    def add_to_kml(self, kml):
        """
        Adds the boundary to the given KML object.

        :param kml: KML object to be modified
        :type kml: :class:`simplekml.Kml`
        :rtype: list of :class:`simplekml.Polygon` objects
        """
        return

    @abstractmethod
    def get_sets_of_exterior_coordinates(self):
        """
        Extracts the exterior coordinates from each constituent polygon and returns them as a list.

        :return: list of (lats, lons) pairs; lats and lons are each lists of floats
        """
        return


class BoundaryShapefile(Boundary):
    """
    :class:`Boundary` class specifically designed for use with ESRI shapefiles. Simply give the \*.shp
    file as the boundary filename.
    """

    def __init__(self, *args, **kwargs):
        super(BoundaryShapefile, self).__init__(*args, **kwargs)
        self._read_shapefile()

    def _read_shapefile(self):
        """
        Read the shapefile specified by :meth:`boundary_filename`. Provides support for multi-part polygons.
        """
        filename = self.boundary_filename()
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
                    self.log.error("Error reading in %s: %s" % (filename, str(e)))

        self._geometries = self._filter_geometries(geometries_and_properties)

    def get_sets_of_exterior_coordinates(self):
        polygons = []
        for geometry in self._geometries:
            if isinstance(geometry, shapely.geometry.polygon.Polygon):
                polygons.append(geometry)
            elif isinstance(geometry, shapely.geometry.multipolygon.MultiPolygon):
                for poly in geometry:
                    polygons.append(poly)

        sets_of_coordinates = []
        for polygon in polygons:
            e = polygon.exterior
            (lons, lats) = e.coords.xy
            sets_of_coordinates.append((lats, lons))

        return sets_of_coordinates

    def add_to_kml(self, kml):
        added_polys = []
        for (lats, lons) in self.get_sets_of_exterior_coordinates():
            coords = zip(lons, lats)
            coords.append(coords[0])    # close the polygon

            poly = kml.newpolygon()
            poly.outerboundaryis.coords = reversed(coords)
            added_polys.append(poly)

        return added_polys

    def _omitted_shapes(self):
        """
        This function, in conjunction with :meth:`_filter_geometries` and :meth:`_geometry_name_field_str:, removes any
        unwanted shapes from the shapefile. This function is meant to be overridden in order to provide customization.
        By default, no shapes are removed.

        :return: the name (e.g. "Hawaii") of an entity that should be omitted when reading the shapefile
        :rtype: list of strings
        """
        return []

    @abstractmethod
    def _geometry_name_field_str(self):
        """
        This function, in conjunction with :meth:`_filter_geometries` and :meth:`_omitted_shapes:, removes any
        unwanted shapes from the shapefile. This function is meant to be overridden in order to provide customization.
        The return value is not used by :meth:`_filter_geometries` in the event that :meth:`_omitted_shapes` returns
        an empty list.

        :return: name of the field in the shapefile which gives the name of the shape (e.g. "NAME")
        :rtype: string
        """
        pass

    def _filter_geometries(self, geometries_and_properties):
        """
        This function, in conjunction with :meth:`_filter_geometries` and :meth:`_omitted_shapes:, removes any
        unwanted shapes from the shapefile. This function may be overridden in order to provide customization.

        :param geometries_and_properties:
        :return:
        """

        omitted_shapes = self._omitted_shapes()

        if len(omitted_shapes) == 0:
            return [geom for (geom,_) in geometries_and_properties]

        name_field = self._geometry_name_field_str()

        return [geom for (geom, properties) in geometries_and_properties if \
                properties[name_field] not in omitted_shapes]


class BoundaryContinentalUnitedStatesWithStateBoundaries(BoundaryShapefile):
    """
    :class:`Boundary` describing the continental United States.

    Data source: https://www.census.gov/geo/maps-data/data/cbf/cbf_state.html
    http://www.census.gov/geo/maps-data/data/tiger-cart-boundary.html
    """

    def boundary_filename(self):
        base_dir = configuration.paths['UnitedStates']['boundaries']
        return path.join(base_dir, "cb_2013_us_state_500k", "cb_2013_us_state_500k.shp")

    def _omitted_shapes(self):
        return ["Hawaii", "Alaska", "Puerto Rico", "American Samoa", "Guam",
                "Commonwealth of the Northern Mariana Islands", "United States Virgin Islands"]

    def _geometry_name_field_str(self):
        return "NAME"


class BoundaryUnitedStates(BoundaryShapefile):
    # http://www.census.gov/geo/maps-data/data/cbf/cbf_nation.html

    def boundary_filename(self):
        base_dir = configuration.paths['UnitedStates']['boundaries']
        return path.join(base_dir, "cb_2013_us_nation_20m", "cb_2013_us_nation_20m.shp")

    def _geometry_name_field_str(self):
        return "NAME"


class BoundaryContinentalUnitedStates(BoundaryUnitedStates):
    """
    This class is identical to :class:`BoundaryUnitedStates` but it excludes any polygons outside
    of the following bounding box:

     - West_Bounding_Coordinate: -124.762451  -> -124.77
     - East_Bounding_Coordinate: -66.791978   -> -66
     - North_Bounding_Coordinate: 49.373047   -> 49.38
     - South_Bounding_Coordinate: 24.501658   -> 24.5

     .. warning:: This will temporarily be the same as :class:`BoundaryUnitedStates`.

    Its output is identical to :class:`BoundaryContinentalUnitedStatesWithStateBoundaries` but it is
    substantially faster.
    """

    def __init__(self, *args, **kwargs):
        super(BoundaryContinentalUnitedStates, self).__init__(*args, **kwargs)
        # self._remove_non_continental_parts()      # TODO: add this back in

    # def _remove_non_continental_parts(self):
    #     # def filter_function(part):
    #     #     first_point = part[0]
    #     #     lat = first_point[1]
    #     #     lon = first_point[0]
    #     #     return (24.5 <= lat <= 49.38) and (-124.77 <= lon <= -66)
    #
    #     # def filter_function_with_shapely(part):
    #     #     first_point = part[0]
    #     #     lat = first_point[1]
    #     #     lon = first_point[0]
    #     #     return (24.5 <= lat <= 49.38) and (-124.77 <= lon <= -66)
    #
    #
    #     # for bp in self._boundary_parts:
    #     #     bp.filter_parts(filter_function)
    #
    #     pass

    def _geometry_name_field_str(self):
        return "NAME"

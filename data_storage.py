from custom_logging import getModuleLogger
import numpy
from map import Map
import simplekml


class DataPointGrid(object):
    """Keeps track of DataPoints whose (latitude, longitude)s naturally belong on a grid. Two-dimensional."""
    def __getstate__(self):
        print self.__dict__
        #self.__delattr__(self, log)
        del self.log
        return self.__dict__
    def __setstate__(self, d):
        self.__dict__.update(d)
        self.log = getModuleLogger(self)

    # matrix: m = [ 1 2 3
    #               4 5 6
    #               7 8 9 ]
    #
    # m[0,0] = m[0][0] = 1
    # m[0,1] = 2
    # m[1,0] = 4

    # def __init__(self, initial_points, latitude_bounds, longitude_bounds, num_latitude_divisions, num_longitude_divisions):
    #     super(DataPointGrid, self).__init__()

    def __init__(self):
        self.log = getModuleLogger(self)


    @classmethod
    def from_grid_specification(cls, latitude_bounds, longitude_bounds, num_latitude_divisions, num_longitude_divisions):
        """
        :param latitude_bounds: (min_latitude, max_latitude)
        :param longitude_bounds: (min_longitude, max_longitude)
        :param num_latitude_divisions:
        :param num_longitude_divisions:
        :return:
        """
        obj = cls()
        obj._initialize_grid(latitude_bounds, longitude_bounds, num_latitude_divisions, num_longitude_divisions)
        return obj

    @classmethod
    def get_copy_of(cls, other_grid):
        """
        Uses everything from :param other_grid: except that the values are populated from :matrix:.
        :param other_grid:
        :type other_grid: :class:`DataPointGrid`
        :param matrix:
        :type matrix: :class:`numpy.matrix`
        :return:
        :rtype: :class:`DataPointGrid`
        """
        obj = cls.from_grid_specification(other_grid._latitude_bounds, other_grid._longitude_bounds,
                                          other_grid._num_latitude_divisions, other_grid._num_longitude_divisions)
        return obj

    @classmethod
    def from_existing_grid(cls, other_grid, matrix):
        """
        Uses everything from :param other_grid: except that the values are populated from :matrix:.
        :param other_grid:
        :type other_grid: :class:`DataPointGrid`
        :param matrix:
        :type matrix: :class:`numpy.matrix`
        :return:
        :rtype: :class:`DataPointGrid`
        """
        obj = cls.from_grid_specification(other_grid._latitude_bounds, other_grid._longitude_bounds,
                                          other_grid._num_latitude_divisions, other_grid._num_longitude_divisions)
        obj.mutable_matrix = matrix
        return obj


    def _initialize_grid(self, latitude_bounds, longitude_bounds, num_latitude_divisions, num_longitude_divisions, data_type=float):
        self.log.debug("Creating grid:\nLatitude bounds: (%f, %f) (%d divisions)\nLongitude bounds: (%f, %f) (%d divisions)" % (latitude_bounds[0], latitude_bounds[1], num_latitude_divisions, longitude_bounds[0], longitude_bounds[1], num_longitude_divisions))

        (min_lat, max_lat) = latitude_bounds
        if min_lat > max_lat:
            raise ValueError("Max. latitude should be greater than min. latitude")

        (min_lon, max_lon) = longitude_bounds
        if min_lon > max_lon:
            raise ValueError("Max. longitude should be greater than min. longitude")

        self._latitude_bounds = latitude_bounds
        self._longitude_bounds = longitude_bounds
        self._num_latitude_divisions = num_latitude_divisions
        self._num_longitude_divisions = num_longitude_divisions

        self._latitudes = numpy.linspace(min_lat, max_lat, num=num_latitude_divisions)
        self._longitudes = numpy.linspace(min_lon, max_lon, num=num_longitude_divisions)

        self._latitude_index_dict = self._convert_list_to_dict(self._latitudes)
        self._longitude_index_dict = self._convert_list_to_dict(self._longitudes)

        self._matrix = numpy.empty((num_latitude_divisions, num_longitude_divisions), dtype=data_type )
        self.reset_all_values()


    def _convert_list_to_dict(self, user_list):
        output_dict = {}
        for (index, value) in enumerate(user_list):
            output_dict[value] = index
        return output_dict

    def get_latitude_index(self, latitude):
        """
        :param latitude: latitude value in decimal degrees
        :type latitude: float
        :rtype: integer or None
        :return: index such that self.latitudes[index] = latitude (returns None if latitude not found)
        """
        if latitude in self._latitude_index_dict:
            return self._latitude_index_dict[latitude]
        else:
            self.log.error("Latitude not found: %f" % latitude)
            return None


    def get_longitude_index(self, longitude):
        """
        :param longitude: longitude value in decimal degrees
        :type longitude: float
        :rtype: integer or None
        :return: index such that self.longitudes[index] = longitude (returns None if longitude not found)
        """
        if longitude in self._longitude_index_dict:
            return self._longitude_index_dict[longitude]
        else:
            self.log.error("Longitude not found: %f" % longitude)
            return None

    @property
    def mutable_matrix(self):
        """This function is useful for performing operations on the entire grid.

        :rtype: :class:`numpy.matrix`
        :return: matrix used for storage
        """
        return self._matrix

    def get_matrix_copy(self):
        """

        :return:
        """
        return self._matrix.copy()

    def reset_all_values(self, fill_value=numpy.NaN):
        """

        :param fill_value:
        :return:
        """
        self._matrix[:] = fill_value

    # @doc_inherit
    # def add_point(self, location):
    #     existing_point = self.g

    @property
    def latitudes(self):
        """Latitude values which define the matrix."""
        return self._latitudes

    @property
    def longitudes(self):
        """Longitude values which define the matrix."""
        return self._longitudes

    def get_value_by_location(self, location):
        """
        :param location: (latitude, longitude)
        :type location: tuple of floats
        :return: the data corresponding to that location
        """
        try:
            (latitude_index, longitude_index) = self.get_indices_from_location(location)
        except ValueError:
            return None

        return self.get_value_by_index(latitude_index, longitude_index)

    def get_indices_from_location(self, location):
        """Determine the indices of the grid which correspond to the given location."""
        (latitude, longitude) = location
        latitude_index = self.get_latitude_index(latitude)
        longitude_index = self.get_longitude_index(longitude)

        if latitude_index is None or longitude_index is None:
            self.log.error("Could not get value: location not found in grid")
            raise ValueError
        else:
            return (latitude_index, longitude_index)

    def get_latitude_by_index(self, index):
        """Inverse function of :meth:`get_latitude_index`.

        :param index:
        :type index: integer
        :return: latitude such that index == get_latitude_index(latitude)
        :rtype: float
        """
        return self._latitudes[index]

    def get_longitude_by_index(self, index):
        """Inverse function of :meth:`get_longitude_index`.

        :param index:
        :type index: integer
        :return: longitude such that index == get_longitude_index(longitude)
        :rtype: float
        """
        return self._longitudes[index]


    def get_value_by_index(self, latitude_index, longitude_index):
        """Get the value of the grid at the specified indices."""
        return self._matrix[latitude_index][longitude_index]

    def set_value_by_index(self, latitude_index, longitude_index, new_value):
        """Set the value of the grid at the specified indices."""
        self._matrix[latitude_index][longitude_index] = new_value

    def set_value_by_location(self, location, new_value):
        """
        Sets the value of the DataPoint(s) at that location. If unsuccessful (return
        value False), the state of related data is not guaranteed.

        :param location: (latitude, longitude)
        :type location: tuple
        :rtype: boolean
        :return: True if successful
        """
        try:
            (latitude_index, longitude_index) = self.get_indices_from_location(location)
        except ValueError:
            return False

        #self._matrix[latitude_index][longitude_index] = new_value
        self.set_value_by_index(latitude_index, longitude_index, new_value)
        return True


    def grids_are_comparable(self, other_grid):
        """Tests grids for comparability (i.e. are they describing the same points?).

        :param other_grid:
        :type other_grid: :class:`DataPointGrid`
        :return: True if the grids use the same coordinates and False otherwise
        :rtype: boolean
        """
        if not isinstance(other_grid, DataPointGrid):
            raise ValueError("Expected a DataPointGrid")

        if not (self._latitude_bounds == other_grid._latitude_bounds):
            self.log.error("Latitude bounds are not equal: (%f, %f) vs. (%f, %f)" % (self._latitude_bounds[0],
                                                                                     self._latitude_bounds[1],
                                                                                     other_grid._latitude_bounds[0],
                                                                                     other_grid._latitude_bounds[1]))
            return False

        if not (self._longitude_bounds == other_grid._longitude_bounds):
            self.log.error("Longitude bounds are not equal: (%f, %f) vs. (%f, %f)" % (self._longitude_bounds[0],
                                                                                     self._longitude_bounds[1],
                                                                                     other_grid._longitude_bounds[0],
                                                                                     other_grid._longitude_bounds[1]))
            return False

        if not (self._num_latitude_divisions == other_grid._num_latitude_divisions):
            self.log.error("Number of latitude divisions is not equal: %d vs. %d" % (self._num_latitude_divisions,
                                                                                     other_grid._num_latitude_divisions))
            return False

        if not (self._num_longitude_divisions == other_grid._num_longitude_divisions):
            self.log.error("Number of longitude divisions is not equal: %d vs. %d" % (self._num_longitude_divisions,
                                                                                     other_grid._num_longitude_divisions))
            return False

        return True

    def combine_grids_with_function(self, other_grid, function):
        """Returns a new :class:`DataPointGrid` where each point is the output
        of calling function(this_point, other_point). Returns None upon error.

        Does not modify the data in either grid.

        :param other_grid:
        :type other_grid: :class:`DataPointGrid`
        :param function: handle to a function taking exactly two arguments of type :class:`DataPoint`
        :rtype: :class:`DataPointCollection` matching this one or None
        :return:
        """
        if not self.grids_are_comparable(other_grid):
            raise TypeError("Grids are not comparable")

        new_grid = DataPointGrid.get_copy_of(self)
        new_grid.reset_all_values()

        dimensions = self.mutable_matrix.shape

        for latitude_index in range(0, dimensions[0]):
            for longitude_index in range(0, dimensions[1]):
                new_value = function( self.get_value_by_index(latitude_index, longitude_index), other_grid.get_value_by_index(latitude_index, longitude_index) )
                new_grid.set_value_by_index(latitude_index, longitude_index, new_value)

        return new_grid


    def elementwise_multiply_grids(self, other_grid):
        """

        :param other_grid:
        :return:
        """
        if not self.grids_are_comparable(other_grid):
            raise TypeError("Grids are not comparable")

        new_grid = DataPointGrid.get_copy_of(self)
        new_grid.mutable_matrix = numpy.multiply(self.mutable_matrix, other_grid.mutable_matrix)

        return new_grid


    def make_map(self, transformation=None):
        """Return a :class:`map.Map` with the data from this grid. Please refer to :meth:`map.Map.__init__` for more
        information on transformations."""
        # make_map(self._matrix)
        if transformation is None:
            return Map(self._matrix)
        else:
            return Map(self._matrix, transformation = transformation)


    def export_to_kml(self, filename, geometry_modification_function=None, include_polygon_function=None, save=True):

        latitude_width = abs(self._latitudes[1] - self._latitudes[0])
        longitude_width = abs(self._longitudes[1] - self._longitudes[0])

        def make_box(kml, center_lat, center_lon, value):

            if include_polygon_function is not None and not include_polygon_function(value):
                return

            poly = kml.newpolygon()

            # (0, 0), (1, 1), (1, 0)])
            max_lat = center_lat + latitude_width/2
            min_lat = center_lat - latitude_width/2
            max_lon = center_lon + longitude_width/2
            min_lon = center_lon - longitude_width/2
            # poly.outerboundaryis = [ (min_lon, min_lat), (min_lon, max_lat),
            #     (max_lon, min_lat), (max_lon, max_lat)]
            poly.outerboundaryis = [ (min_lon, max_lat), (max_lon, max_lat), (max_lon, min_lat), (min_lon, min_lat)]

            poly.description = str(value)
            # poly.style.polystyle.color = simplekml.Color.red
            # poly.style.polystyle.outline = 1

            if geometry_modification_function is not None:
                geometry_modification_function(poly, value)


        kml = simplekml.Kml()

        for (lat_idx, lat) in enumerate(self._latitudes):
            for (lon_idx, lon) in enumerate(self._longitudes):
                value = self.get_value_by_index(lat_idx, lon_idx)
                make_box(kml, lat, lon, value)

        if save:
            kml.save(filename)

        return kml



class GridCollection(object):   # TODO: write this
    """Collection of several grids.
    """
    def __init__(self):
        pass

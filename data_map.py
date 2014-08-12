from custom_logging import getModuleLogger
import numpy
from map import Map
import simplekml


class DataMap2D(object):
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
    #     super(DataMap2D, self).__init__()

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
        Creates a copy of the grid. The internal matrix will also be copied.

        :param other_grid:
        :type other_grid: :class:`DataMap2D`
        :return:
        :rtype: :class:`DataMap2D`
        """
        obj = cls.from_grid_specification(other_grid._latitude_bounds, other_grid._longitude_bounds,
                                          other_grid._num_latitude_divisions, other_grid._num_longitude_divisions)
        obj.mutable_matrix = other_grid.mutable_matrix
        return obj

    @classmethod
    def from_existing_grid(cls, other_grid, matrix):
        """
        Uses everything from :param other_grid: except that the values are copied from :matrix:. If :matrix: is a
        scalar, all values will be initialized to that value.

        :param other_grid:
        :type other_grid: :class:`DataMap2D`
        :param matrix:
        :type matrix: :class:`numpy.matrix`
        :return:
        :rtype: :class:`DataMap2D`
        """
        obj = cls.from_grid_specification(other_grid._latitude_bounds, other_grid._longitude_bounds,
                                          other_grid._num_latitude_divisions, other_grid._num_longitude_divisions)
        if isinstance(matrix, numpy.matrix):
            obj.mutable_matrix = matrix
        else:
            obj.reset_all_values(matrix)
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
        """
        Internal data store for the :class:`DataMap2D`.

        :rtype: :class:`numpy.matrix`
        :return: matrix used for storage
        """
        return self._matrix

    @mutable_matrix.setter
    def mutable_matrix(self, new_matrix):
        self._matrix = new_matrix.copy()

    def get_matrix_copy(self):
        """
        Returns a copy of the internal matrix.
        """
        return self._matrix.copy()

    def reset_all_values(self, fill_value=numpy.NaN):
        """
        Resets all values of the :class:`DataMap2D` to the specified `fill_value`.
        """
        self._matrix[:] = fill_value

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

        self.set_value_by_index(latitude_index, longitude_index, new_value)
        return True


    def grid_is_comparable(self, other_grid):
        """Tests grids for comparability (i.e. are they describing the same points?).

        :param other_grid:
        :type other_grid: :class:`DataMap2D`
        :return: True if the grids use the same coordinates and False otherwise
        :rtype: boolean
        """
        if not isinstance(other_grid, DataMap2D):
            raise ValueError("Expected a DataMap2D")

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
        """Returns a new :class:`DataMap2D` where each point is the output
        of calling function(this_point, other_point). Returns None upon error.

        Does not modify the data in either grid.

        :param other_grid:
        :type other_grid: :class:`DataMap2D`
        :param function: handle to a function taking exactly two arguments of type :class:`DataPoint`
        :rtype: :class:`DataPointCollection` matching this one or None
        :return:
        """
        if not self.grid_is_comparable(other_grid):
            raise TypeError("Grids are not comparable")

        new_grid = DataMap2D.get_copy_of(self)
        new_grid.reset_all_values()

        dimensions = self.mutable_matrix.shape

        for latitude_index in range(0, dimensions[0]):
            for longitude_index in range(0, dimensions[1]):
                new_value = function( self.get_value_by_index(latitude_index, longitude_index), other_grid.get_value_by_index(latitude_index, longitude_index) )
                new_grid.set_value_by_index(latitude_index, longitude_index, new_value)

        return new_grid


    def elementwise_multiply_grids(self, other_grid):
        """
        Multiplies the two grids element-wise (i.e. at each location) and returns a new :class:`DataMap2D`
        containing the result. The grids must be comparable (i.e. have the same lat/long bounds).
        """
        if not self.grid_is_comparable(other_grid):
            raise TypeError("Grids are not comparable")

        new_grid = DataMap2D.get_copy_of(self)
        new_grid.mutable_matrix = numpy.multiply(self.mutable_matrix, other_grid.mutable_matrix)

        return new_grid


    def make_map(self, transformation=None):
        """Return a :class:`map.Map` with the data from this grid. Please refer to :meth:`map.Map.__init__` for more
        information on transformations."""
        # make_map(self._matrix)
        if transformation is None:
            return Map(self)
        else:
            return Map(self, transformation = transformation)


    def add_to_kml(self, kml=None, geometry_modification_function=None, include_polygon_function=None, filename=None, save=True):
        """
        Add the data to a KML object for plotting with e.g. Google Earth.

        :param kml: existing KML object (created if none given)
        :type kml: :class:`simplekml.Kml`
        :param geometry_modification_function: function which modifies each KML element after creation (two \
        parameters: KML polygon and the value of the pixel)
        :type geometry_modification_function: function handle
        :param include_polygon_function: function which determines if the polygon should be included based on the \
        value of the pixel (one parameter: value of the pixel; returns True if the polygon should be included)
        :type include_polygon_function: function handle
        :param filename: output filename
        :type filename: str
        :param save: if True, the KML is saved with the given filename
        :type save: bool
        :return: KML object
        :rtype: :class:`simplekml.Kml`
        """

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

        kml = kml or simplekml.Kml()

        for (lat_idx, lat) in enumerate(self._latitudes):
            for (lon_idx, lon) in enumerate(self._longitudes):
                value = self.get_value_by_index(lat_idx, lon_idx)
                make_box(kml, lat, lon, value)

        if save:
            if filename is None:
                self.log.error("Could not save KML: no filename given")
            else:
                kml.save(filename)

        return kml

    def save_to_file(self, filename):       # TODO: write this function
            pass

    def load_from_file(self, filename):     # TODO: write this function
        pass


class DataMap2DContinentalUnitedStates(DataMap2D):
    """:class:`DataMap2D` with presets bounds for the continental United States."""
    @classmethod
    def make_grid(cls, num_latitude_divisions=200, num_longitude_divisions=300):
        latitude_bounds = [24.5, 49.38]
        longitude_bounds = [-124.77, -66]
        return DataMap2D.from_grid_specification(latitude_bounds, longitude_bounds, num_latitude_divisions, num_longitude_divisions)

class DataMap2DBayArea(DataMap2D):
    """:class:`DataMap2D` with presets bounds for the Bay Area of the United States."""
    @classmethod
    def make_grid(cls, num_latitude_divisions=50, num_longitude_divisions=50):
        latitude_bounds = [37.2, 38.4]
        longitude_bounds = [-123.2, -121]
        return DataMap2D.from_grid_specification(latitude_bounds, longitude_bounds, num_latitude_divisions, num_longitude_divisions)

class DataMap2DWisconsin(DataMap2D):
    """:class:`DataMap2D` with presets bounds for Wisconsin, United States."""
    @classmethod
    def make_grid(cls, num_latitude_divisions=50, num_longitude_divisions=50):
        latitude_bounds = [42.5, 47]
        longitude_bounds = [-93.5, -87]
        return DataMap2D.from_grid_specification(latitude_bounds, longitude_bounds, num_latitude_divisions, num_longitude_divisions)



class DataMap3D(object):
    """Collection of one or more :class:`DataMap2D` objects. Provides convenient setter and getter functions for these
    objects.
    """
    def __init__(self):
        self.log = getModuleLogger(self)

    @classmethod
    def from_DataMap2D(cls, template_data_map_2d, layer_descr_list):
        """
        Creates a :class:`DataMap3D` object by replicating the :template_data_map_2d: object `len(layer_descr_list)`
        times.

        :param template_data_map_2d: a data map which provides the default values (e.g. latitude and longitude bounds, \
        number of divisions) for each layer of the map
        :type template_data_map_2d: :class:`DataMap2D`
        :param layer_descr_list: description (key) for each layer; must be unique
        :type layer_descr_list: list
        :return:
        :rtype: :class:`DataMap3D`
        """
        obj = cls()
        obj._initialize_layers(template_data_map_2d, layer_descr_list)
        return obj

    def _initialize_layers(self, template_data_map_2d, layer_descr_list):
        """Internal function to create the layers from the template and the list of descriptions."""
        self._layers = {}
        self._layer_descr_list = layer_descr_list

        for layer_descr in layer_descr_list:
            self._layers[layer_descr] = DataMap2D.get_copy_of(template_data_map_2d)

        if len(self._layers.keys()) is not len(layer_descr_list):
            self.log.warning("Incorrect number of layers created; duplicate keys?")

    def get_layer(self, layer_descr):
        """
        Retrieve a layer based on its description (key).
        """
        try:
            return self._layers[layer_descr]
        except Exception as e:
            self.log.error("Could not retrieve layer: " + str(e))
            return

    def get_all_layers_at_index_as_list(self, latitude_index, longitude_index):
        """
        Returns a list containing the value of each layer at the specified location. The list is ordered according to
        the original `layer_descr_list`.

        See also: :meth:`set_all_layers_at_index_from_list`.
        """
        value_dict = self.get_all_layers_at_index_as_dict(latitude_index, longitude_index)
        value_list = []
        for layer_descr in self._layer_descr_list:
            value_list.append(value_dict[layer_descr])
        return value_list

    def get_all_layers_at_index_as_dict(self, latitude_index, longitude_index):
        """
        Returns a dictionary containing the value of each layer at the specified location. The keys of the dictionary
        are taken from the original `layer_descr_list`.

        See also: :meth:`set_all_layers_at_index_from_dict`.
        """
        value_dict = {}
        for (layer_descr, layer) in self._layers.iteritems():
            value_dict[layer_descr] = layer.get_value_by_index(latitude_index, longitude_index)
        return value_dict

    def get_all_layers_at_location_as_list(self, location):
        """
        Returns a list containing the value of each layer at the specified location. The list is ordered according to
        the original `layer_descr_list`.
        """
        some_layer = self._layers.values()[0]
        (latitude_index, longitude_index) = some_layer.get_indices_from_location(location)
        return self.get_all_layers_at_index_as_list(latitude_index, longitude_index)

    def get_all_layers_at_location_as_dict(self, location):
        """
        Returns a dictionary containing the value of each layer at the specified location. The keys of the dictionary
        are taken from the original `layer_descr_list`.
        """
        some_layer = self._layers.values()[0]
        (latitude_index, longitude_index) = some_layer.get_indices_from_location(location)
        return self.get_all_layers_at_index_as_dict(latitude_index, longitude_index)

    def set_all_layers_at_index_from_list(self, latitude_index, longitude_index, list_of_values):
        """
        Sets the value of each layer at the specified location. The list is assumed to be ordered according to the
        original `layer_descr_list`.

        See also: :meth:`get_all_layers_at_index_as_list`.
        """
        if len(list_of_values) is not len(self._layer_descr_list):
            self.log.error("Could not set values: expected %d values but got %d." % (len(self._layer_descr_list),
                                                                                     len(list_of_values)))
            return

        dict_of_values = {}
        for (descr, value) in zip(self._layer_descr_list, list_of_values):
            dict_of_values[descr] = value
        self.set_all_layers_at_index_from_dict(latitude_index, longitude_index, dict_of_values)

    def set_all_layers_at_index_from_dict(self, latitude_index, longitude_index, dict_of_values):
        """
        Sets the value of the layers at the specified location. The keys of the dictionary must correspond to the
        original `layer_descr_list`.

        See also: :meth:`get_all_layers_at_index_as_dict`.
        """
        for (descr, value) in dict_of_values:
            layer = self.get_layer(descr)
            if layer is None:
                self.log.error("Could not set layer '%s': layer was not retrieved." % descr)
                continue
            layer.set_value_by_index(latitude_index, longitude_index, value)

    def _add_layers(self, list_of_layers):
        """
        Internal helper function to add a generic list of layers.

        :type list_of_layers: list of :class:`DataMap2D` objects
        :rtype: :class:`DataMap2D`
        """
        if any(layer is None for layer in list_of_layers):
            self.log.error("Can't add layers: at least one is None")
            return

        destination_data_map = DataMap2D.from_existing_grid(list_of_layers[0], 0)

        for layer in list_of_layers:
            destination_data_map.mutable_matrix += layer.mutable_matrix

        return destination_data_map

    def sum_all_layers(self):
        """
        Sums all layers element-wise (i.e. determines the sum across layers at each location).

        :rtype: :class:`DataMap2D`
        """
        return self._add_layers(self._layers.values())

    def sum_subset_of_layers(self, layer_descrs):
        """
        Sums a subset of layers element-wise (i.e. determines the sum across layers at each location).

        :param layer_descrs: layer descriptions (keys) corresponding to those in the original `layer_descr_list`.
        :rtype: :class:`DataMap2D`
        """
        return self._add_layers([self.get_layer(descr) for descr in layer_descrs])

    def reset_all_values(self, fill_value=numpy.NaN):
        """
        Resets all values of all layers to `fill_value`.
        """
        for layer in self._layers.values():
            layer.reset_all_values(fill_value)

    def save_to_file(self, filename):       # TODO: write this function
        pass

    def load_from_file(self, filename):     # TODO: write this function
        pass

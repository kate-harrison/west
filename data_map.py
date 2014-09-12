from custom_logging import getModuleLogger
import numpy
from map import Map
import simplekml
import pickle
import helpers


class DataMap2D(object):
    """Keeps track of DataPoints whose (latitude, longitude)s naturally belong on a grid. Two-dimensional."""
    def __init__(self):
        self.log = getModuleLogger(self)

    @classmethod
    def from_specification(cls, latitude_bounds, longitude_bounds, num_latitude_divisions, num_longitude_divisions):
        """
        :param latitude_bounds: (min_latitude, max_latitude)
        :param longitude_bounds: (min_longitude, max_longitude)
        :param num_latitude_divisions: number of latitude points per longitude
        :type num_latitude_divisions: int
        :param num_longitude_divisions: number of longitude points per latitude
        :type num_longitude_divisions: int
        :return:
        :rtype: :class:`DataMap2D`
        """
        obj = cls()
        obj._initialize(latitude_bounds, longitude_bounds, num_latitude_divisions, num_longitude_divisions)
        return obj

    @classmethod
    def get_copy_of(cls, other_datamap2d):
        """
        Creates a copy of the :class:`DataMap2D`. The internal matrix will also be copied.

        :param other_datamap2d:
        :type other_datamap2d: :class:`DataMap2D`
        :return:
        :rtype: :class:`DataMap2D`
        """
        obj = cls.from_specification(other_datamap2d._latitude_bounds, other_datamap2d._longitude_bounds,
                                     other_datamap2d._num_latitude_divisions,
                                     other_datamap2d._num_longitude_divisions)
        obj.mutable_matrix = other_datamap2d.mutable_matrix
        return obj

    @classmethod
    def from_existing_DataMap2D(cls, other_datamap2d, matrix):
        """
        Uses everything from ``other_datamap2d`` except that the values are copied from ``matrix``. If ``matrix`` is a
        scalar, all values will be initialized to that value.

        :param other_datamap2d:
        :type other_datamap2d: :class:`DataMap2D`
        :param matrix:
        :type matrix: :class:`numpy.matrix`
        :return:
        :rtype: :class:`DataMap2D`
        """
        obj = cls.from_specification(other_datamap2d._latitude_bounds, other_datamap2d._longitude_bounds,
                                     other_datamap2d._num_latitude_divisions,
                                     other_datamap2d._num_longitude_divisions)
        if isinstance(matrix, numpy.matrix):
            obj.mutable_matrix = matrix
        else:
            obj.reset_all_values(matrix)
        return obj

    def _initialize(self, latitude_bounds, longitude_bounds, num_latitude_divisions, num_longitude_divisions,
                    data_type=float):
        self.log.debug("Creating DataMap2D:" +
                       "\nLatitude bounds: (%f, %f) (%d divisions)\nLongitude bounds: (%f, %f) (%d divisions)"
                       % (latitude_bounds[0], latitude_bounds[1], num_latitude_divisions, longitude_bounds[0],
                          longitude_bounds[1], num_longitude_divisions))

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

        self._matrix = numpy.empty((num_latitude_divisions, num_longitude_divisions), dtype=data_type)
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
        """Determine the indices of the :class:`DataMap2D` which correspond to the given location."""
        (latitude, longitude) = location
        latitude_index = self.get_latitude_index(latitude)
        longitude_index = self.get_longitude_index(longitude)

        if latitude_index is None or longitude_index is None:
            self.log.error("Could not get value: location not found in DataMap2D")
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
        """Get the value of the :class:`DataMap2D` at the specified indices."""
        return self._matrix[latitude_index][longitude_index]

    def set_value_by_index(self, latitude_index, longitude_index, new_value):
        """Set the value of the :class:`DataMap2D` at the specified indices."""
        self._matrix[latitude_index][longitude_index] = new_value

    def set_value_by_location(self, location, new_value):
        """
        Sets the value of the :class:`DataMap2D` at that location. If unsuccessful (return
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

    def update_all_values_via_function(self, update_function, verbose=False):
        """
        Updates each pixel in the :class:`DataMap2D` according to ``update_function``. The return value from the
        update function is used as the new value for that pixel, except if the value is None; in that case, no update
        is performed.

        ``update_function`` should have the following signature::

            def update_function(latitude, longitude, latitude_index, longitude_index, current_value):
                ...
                return new_value_for_pixel      # may also return None if no update is desired

        :param update_function: function used to update the values
        :type update_function: function object
        :param verbose: if True, progress updates will be logged (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: None
        """
        for (lat_idx, lat) in enumerate(self.latitudes):
            if verbose and lat_idx % 10 == 0:
                self.log.info("Latitude number: %d" % lat_idx)
            for (lon_idx, lon) in enumerate(self.longitudes):
                current_value = self.get_value_by_index(lat_idx, lon_idx)
                new_value = update_function(lat, lon, lat_idx, lon_idx, current_value)
                if new_value is not None:
                    self.set_value_by_index(lat_idx, lon_idx, new_value)

    def datamap_is_comparable(self, other_datamap2d):
        """Tests two :class:`DataMap2D` objects for comparability (i.e. are they describing the same points?).

        :param other_datamap2d:
        :type other_datamap2d: :class:`DataMap2D`
        :return: True if the objects use the same coordinates and False otherwise; error message
        :rtype: boolean, str
        """
        if not isinstance(other_datamap2d, DataMap2D):
            return False, "Expected a DataMap2D"

        if not (self._latitude_bounds == other_datamap2d._latitude_bounds):
            return False, "Latitude bounds are not equal: (%f, %f) vs. (%f, %f)" % (self._latitude_bounds[0],
                                                                                    self._latitude_bounds[1],
                                                                                    other_datamap2d._latitude_bounds[0],
                                                                                    other_datamap2d._latitude_bounds[1])

        if not (self._longitude_bounds == other_datamap2d._longitude_bounds):
            return False, "Longitude bounds are not equal: (%f, %f) vs. (%f, %f)" \
                          % (self._longitude_bounds[0], self._longitude_bounds[1],
                          other_datamap2d._longitude_bounds[0], other_datamap2d._longitude_bounds[1])

        if not (self._num_latitude_divisions == other_datamap2d._num_latitude_divisions):
            return False, "Number of latitude divisions is not equal: %d vs. %d" \
                          % (self._num_latitude_divisions, other_datamap2d._num_latitude_divisions)

        if not (self._num_longitude_divisions == other_datamap2d._num_longitude_divisions):
            return False, "Number of longitude divisions is not equal: %d vs. %d" \
                          % (self._num_longitude_divisions, other_datamap2d._num_longitude_divisions)

        return True, None

    def raise_error_if_datamaps_are_incomparable(self, other_datamap2d):
        """Tests two :class:`DataMap2D` objects for comparability (i.e. are they describing the same points?). Raises a
        ValueError if they are incomparable.

        :param other_datamap2d:
        :type other_datamap2d: :class:`DataMap2D`
        """
        comparable, error_msg = self.datamap_is_comparable(other_datamap2d)
        if comparable:
            return
        else:
            raise TypeError(error_msg)

    def combine_datamaps_with_function(self, other_datamap2d, combination_function):
        """Returns a new :class:`DataMap2D` where each point is the output
        of calling ``combination_function(this_point, other_point)``.

        The function signature of ``combination_function`` should be as follows::

            def combination_function(this_value, other_value):
                ...
                return combined_value

        Does not modify the data in either :class:`DataMap2D`.

        :param other_datamap2d:
        :type other_datamap2d: :class:`DataMap2D`
        :param combination_function: handle to a function taking exactly two arguments of type :class:`DataPoint`
        :type combination_function: function object
        :rtype: :class:`DataPointCollection` matching this one or None
        :return:
        """
        self.raise_error_if_datamaps_are_incomparable(other_datamap2d)

        new_datamap2d = DataMap2D.get_copy_of(self)
        new_datamap2d.reset_all_values()

        dimensions = self.mutable_matrix.shape

        for latitude_index in range(0, dimensions[0]):
            for longitude_index in range(0, dimensions[1]):
                new_value = combination_function( self.get_value_by_index(latitude_index, longitude_index),
                                      other_datamap2d.get_value_by_index(latitude_index, longitude_index))
                new_datamap2d.set_value_by_index(latitude_index, longitude_index, new_value)

        return new_datamap2d

    def elementwise_multiply_datamaps(self, other_datamap2d):
        """
        Multiplies the two :class:`DataMap2D` objects element-wise (i.e. at each location) and returns a new
        :class:`DataMap2D` containing the result. The objects must be comparable (i.e. have the same lat/long bounds).
        """
        self.raise_error_if_datamaps_are_incomparable(other_datamap2d)

        new_datamap2d = DataMap2D.get_copy_of(self)
        new_datamap2d.mutable_matrix = numpy.multiply(self.mutable_matrix, other_datamap2d.mutable_matrix)

        return new_datamap2d

#####
#   DATA EXPORT
#####
    def make_map(self, *args, **kwargs):
        """Return a :class:`map.Map` with the data from this :class:`DataMap2D`. Please refer to
        :meth:`map.Map.__init__` for more information."""
        return Map(self, *args, **kwargs)

    def add_to_kml(self, kml=None, geometry_modification_function=None, include_polygon_function=None, filename=None,
                   save=True):
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

            max_lat = center_lat + latitude_width/2
            min_lat = center_lat - latitude_width/2
            max_lon = center_lon + longitude_width/2
            min_lon = center_lon - longitude_width/2
            poly.outerboundaryis = [ (min_lon, max_lat), (max_lon, max_lat), (max_lon, min_lat), (min_lon, min_lat)]

            poly.description = str(value)

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

    def to_pickle(self, filename):
        """
        Save the DataMap2D to a pickle with the specified ``filename``. See also: :meth:`from_pickle`.

        :param filename: destination filename
        :type filename: str
        :return: None
        """
        with open(filename, "w") as f:
            pickle.dump(self, f)

    @classmethod
    def from_pickle(cls, filename):
        """
        Loads the DataMap2D from a pickle with the specified ``filename``. See also: :meth:`to_pickle`.

        :param filename: destination filename
        :type filename: str
        :return:
        :rtype: :class:`DataMap2D`
        """
        with open(filename, "r") as f:
            return pickle.load(f)

    # Helper functions required for pickling
    # Objects with open file descriptors (e.g. logs) cannot be pickled, so we remove the logs when saving
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['log']
        return state

    def __setstate__(self, d):
        self.__dict__.update(d)
#####
#   END DATA EXPORT
#####


#####
#   SUBMAPS
#####
    def generate_submap(self, latitude_bounds, longitude_bounds,
                        generate_even_if_submap_partially_outside_datamap=False):
        """
        Generates a :class:`DataMap2D` which contains a subset of this DataMap2D's coordinates and data. The bounds of
        the resulting submap will be greater than or equal to the bounds given as arguments (i.e. the submap will
        contain the bounding points, though not necessarily as points themselves). In other words, the submap will
        represent a region which is at least as large as the bounds given.

        The original map is not altered when generating a submap.

        See also: :meth:`reintegrate_submap`.

        :param latitude_bounds: (min_latitude, max_latitude)
        :param longitude_bounds: (min_longitude, max_longitude)
        :param generate_even_if_submap_partially_outside_datamap: if True, generates the submap closest to the given \
                bounds even if the requested submap is not fully contained in the DataMap2D; if False, a ValueError \
                will be raised if such a request is made. May still generate a ValueError if there is no overlap \
                between the requested submap and the DataMap2D.
        :return: data map which contains a subset of the data in this map
        :rtype: :class:`DataMap2D`
        """
        (min_lat, max_lat) = latitude_bounds
        if min_lat > max_lat:
            raise ValueError("Max. latitude should be greater than min. latitude")

        (min_lon, max_lon) = longitude_bounds
        if min_lon > max_lon:
            raise ValueError("Max. longitude should be greater than min. longitude")

        lower_latitude_index = helpers.find_last_value_below_or_equal(self.latitudes, min_lat)
        lower_longitude_index = helpers.find_last_value_below_or_equal(self.longitudes, min_lon)
        upper_latitude_index = helpers.find_first_value_above_or_equal(self.latitudes, max_lat)
        upper_longitude_index = helpers.find_first_value_above_or_equal(self.longitudes, max_lon)

        if any([index is None for index in
                [lower_latitude_index, lower_longitude_index, upper_latitude_index, upper_longitude_index]]):
            if not generate_even_if_submap_partially_outside_datamap:
                raise ValueError("Given latitude/longitude bounds are out of the strict bounds for this DataMap2D."
                                 " Consider using the 'generate_even_if_submap_partially_outside_datamap' option.")
            elif min_lat > self._latitude_bounds[1] or max_lat < self._latitude_bounds[0] \
                    or min_lon > self._longitude_bounds[1] or max_lon < self._longitude_bounds[0]:
                raise ValueError("There is no overlap between the given latitude/longitude bounds and this DataMap2D.")
            else:   # can assume at most one of the indices in each pair is None
                self.log.debug("Generating a submap which is smaller than the requested latitude/longitude bounds")
                lower_latitude_index = lower_latitude_index or 0
                upper_latitude_index = upper_latitude_index or len(self.latitudes)-1
                lower_longitude_index = lower_longitude_index or 0
                upper_longitude_index = upper_longitude_index or len(self.longitudes)-1


        num_latitude_divisions = upper_latitude_index - lower_latitude_index + 1
        num_longitude_divisions = upper_longitude_index - lower_longitude_index + 1

        actual_latitude_bounds = (self.latitudes[lower_latitude_index], self.latitudes[upper_latitude_index])
        actual_longitude_bounds = (self.longitudes[lower_longitude_index], self.longitudes[upper_longitude_index])

        submap = DataMap2D.from_specification(actual_latitude_bounds, actual_longitude_bounds, num_latitude_divisions,
                                              num_longitude_divisions)

        # Copy the submatrix from this DataMap2D into the submap
        submap.mutable_matrix = self.mutable_matrix[lower_latitude_index:upper_latitude_index+1,
                                lower_longitude_index:upper_longitude_index+1]

        return submap

    def reintegrate_submap(self, submap, integration_function):
        """
        Re-integrates the submap into this map by combining corresponding values according to ``integration_function``.
        The integration function should take two arguments of type :class:`numpy.matrix` and output a
        :class:`numpy.matrix`. The first matrix will contain the current values of this map and the second matrix will
        contain values from the submap. Some examples::

            my_data_map.reintegrate_submap(my_submap, integration_function=lambda x,y: x+y)
            my_data_map.reintegrate_submap(my_submap, integration_function=numpy.logical_or)
            my_data_map.reintegrate_submap(my_submap, integration_function=numpy.maximum)

        .. note:: If the submap is not comparable (i.e. its coordinates are not a subset of this map's coordinates), \
        integration will not be possible. To generate a comparable submap, use :meth:`generate_submap`.

        See also: :meth:`generate_submap`

        :param submap: submap to be reintegrated into this map (submap is not modified)
        :type submap: :class:`DataMap2D`
        :param integration_function: function which dictates how the two matrices should be combined
        :type integration_function: function object
        """

        # Extract indices for the submatrix and do lots of error checking
        if not isinstance(submap, DataMap2D):
            raise TypeError("Expected a DataMap2D")

        lower_latitude_index = helpers.find_first_value_approximately_equal(self.latitudes, submap.latitudes[0])
        lower_longitude_index = helpers.find_first_value_approximately_equal(self.longitudes, submap.longitudes[0])
        if lower_latitude_index is None or lower_longitude_index is None:
            raise ValueError("Submap is not comparable (latitudes and/or longitudes differ)")
        upper_latitude_index = lower_latitude_index + len(submap.latitudes)
        upper_longitude_index = lower_longitude_index + len(submap.longitudes)

        target_latitudes = self.latitudes[lower_latitude_index:upper_latitude_index+1]
        target_longitudes = self.longitudes[lower_longitude_index:upper_longitude_index+1]

        if not helpers.lists_are_almost_equal(submap.latitudes, target_latitudes) or \
                not helpers.lists_are_almost_equal(submap.longitudes, target_longitudes):
            raise ValueError("Submap is not comparable (latitudes and/or longitudes differ)")

        # Update the internal matrix according to the combination function
        self.mutable_matrix[lower_latitude_index:upper_latitude_index,
        lower_longitude_index:upper_longitude_index] = integration_function(
            self.mutable_matrix[lower_latitude_index:upper_latitude_index,
            lower_longitude_index:upper_longitude_index],
            submap.mutable_matrix)
#####
#   END SUBMAPS
#####


class DataMap2DContinentalUnitedStates(DataMap2D):
    """:class:`DataMap2D` with presets bounds for the continental United States."""
    @classmethod
    def create(cls, num_latitude_divisions=200, num_longitude_divisions=300):
        """
        Creates a :class:`DataMap2D` with latitude and longitude bounds tailored to the continental United States.

        :param num_latitude_divisions: number of latitude points per longitude
        :type num_latitude_divisions: int
        :param num_longitude_divisions: number of longitude points per latitude
        :type num_longitude_divisions: int
        :return:
        :rtype: :class:`DataMap2DContinentalUnitedStates`
        """
        latitude_bounds = [24.5, 49.38]
        longitude_bounds = [-124.77, -66]
        return DataMap2D.from_specification(latitude_bounds, longitude_bounds, num_latitude_divisions,
                                            num_longitude_divisions)


class DataMap2DBayArea(DataMap2D):
    """:class:`DataMap2D` with presets bounds for the Bay Area of the United States."""
    @classmethod
    def create(cls, num_latitude_divisions=50, num_longitude_divisions=50):
        """
        Creates a :class:`DataMap2D` with latitude and longitude bounds tailored to the continental United States.

        :param num_latitude_divisions: number of latitude points per longitude
        :type num_latitude_divisions: int
        :param num_longitude_divisions: number of longitude points per latitude
        :type num_longitude_divisions: int
        :return:
        :rtype: :class:`DataMap2DBayArea`
        """
        latitude_bounds = [37.2, 38.4]
        longitude_bounds = [-123.2, -121]
        return DataMap2D.from_specification(latitude_bounds, longitude_bounds, num_latitude_divisions,
                                            num_longitude_divisions)


class DataMap2DWisconsin(DataMap2D):
    """:class:`DataMap2D` with presets bounds for Wisconsin, United States."""
    @classmethod
    def create(cls, num_latitude_divisions=50, num_longitude_divisions=50):
        """
        Creates a :class:`DataMap2D` with latitude and longitude bounds tailored to Wisconsin.

        :param num_latitude_divisions: number of latitude points per longitude
        :type num_latitude_divisions: int
        :param num_longitude_divisions: number of longitude points per latitude
        :type num_longitude_divisions: int
        :return:
        :rtype: :class:`DataMap2DWisconsin`
        """
        latitude_bounds = [42.5, 47]
        longitude_bounds = [-93.5, -87]
        return DataMap2D.from_specification(latitude_bounds, longitude_bounds, num_latitude_divisions,
                                            num_longitude_divisions)


class DataMap3D(object):
    """Collection of one or more :class:`DataMap2D` objects. Provides convenient setter and getter functions for these
    objects.
    """
    def __init__(self):
        self.log = getModuleLogger(self)

    @classmethod
    def from_DataMap2D(cls, template_datamap2d, layer_descr_list):
        """
        Creates a :class:`DataMap3D` object by replicating the :template_datamap2d: object `len(layer_descr_list)`
        times.

        :param template_datamap2d: a data map which provides the default values (e.g. latitude and longitude bounds, \
        number of divisions) for each layer of the map
        :type template_datamap2d: :class:`DataMap2D`
        :param layer_descr_list: description (key) for each layer; must be unique
        :type layer_descr_list: list
        :return:
        :rtype: :class:`DataMap3D`
        """
        obj = cls()
        obj._initialize_layers(template_datamap2d, layer_descr_list)
        return obj

    def _initialize_layers(self, template_datamap2d, layer_descr_list):
        """Internal function to create the layers from the template and the list of descriptions."""
        self._layers = {}
        self._layer_descr_list = layer_descr_list

        datamap_class = template_datamap2d.__class__

        for layer_descr in layer_descr_list:
            self._layers[layer_descr] = datamap_class.get_copy_of(template_datamap2d)

        if len(self._layers.keys()) is not len(layer_descr_list):
            self.log.warning("Incorrect number of layers created; duplicate keys?")

    def _raise_error_if_any_layer_does_not_exist(self, layer_descr_list):
        # TODO: add this to more functions, as needed
        for layer_descr in layer_descr_list:
            if layer_descr not in self._layer_descr_list:
                raise AttributeError("Layer does not exist: %s" % str(layer_descr))

    def get_layer(self, layer_descr):
        """
        Retrieve a layer based on its description (key).
        """
        self._raise_error_if_any_layer_does_not_exist([layer_descr])
        try:
            return self._layers[layer_descr]
        except Exception as e:
            self.log.error("Could not retrieve layer: " + str(e))
            return

    def set_layer(self, layer_descr, new_layer):
        """
        Replace a layer (:class:`DataMap2D`) with a new :class:`DataMap2D` object. The old and new objects must be
        comparable and the layer must already exist.
        """
        self._raise_error_if_any_layer_does_not_exist([layer_descr])

        old_layer = self.get_layer(layer_descr)
        old_layer.raise_error_if_datamaps_are_incomparable(new_layer)

        self._layers[layer_descr] = new_layer

    def get_some_layers_at_index_as_list(self, layer_descr_list, latitude_index, longitude_index):
        """
        Returns a list containing the value of each layer at the specified location. The list is ordered according to
        the given ``layer_descr_list``.

        See also: :meth:`get_all_layers_at_index_as_list`, :meth:`set_all_layers_at_index_from_list`, \
                    :meth:`set_some_layers_at_index_from_list`
        """
        self._raise_error_if_any_layer_does_not_exist(layer_descr_list)

        value_dict = self.get_all_layers_at_index_as_dict(latitude_index, longitude_index)
        value_list = []
        for layer_descr in layer_descr_list:
            value_list.append(value_dict[layer_descr])
        return value_list

    def get_all_layers_at_index_as_list(self, latitude_index, longitude_index):
        """
        Returns a list containing the value of each layer at the specified location. The list is ordered according to
        the original `layer_descr_list`.

        See also: :meth:`get_some_layers_at_index_as_list`, :meth:`set_all_layers_at_index_from_list` \
                    :meth:`set_some_layers_at_index_from_list`
        """
        return self.get_some_layers_at_index_as_list(self._layer_descr_list, latitude_index, longitude_index)

    def get_all_layers_at_index_as_dict(self, latitude_index, longitude_index):
        """
        Returns a dictionary containing the value of each layer at the specified location. The keys of the dictionary
        are taken from the original `layer_descr_list`.

        See also: :meth:`get_all_layers_at_index_as_list`, :meth:`get_some_layers_at_index_as_list`, \
                    :meth:`set_all_layers_at_index_from_dict`.
        """
        value_dict = {}
        for (layer_descr, layer) in self._layers.iteritems():
            value_dict[layer_descr] = layer.get_value_by_index(latitude_index, longitude_index)
        return value_dict

    def get_some_layers_at_location_as_list(self, layer_descr_list, location):
        """
        Returns a list containing the value of each layer at the specified location. The list is ordered according to
        the given `layer_descr_list`.
        """
        some_layer = self._layers.values()[0]
        (latitude_index, longitude_index) = some_layer.get_indices_from_location(location)
        return self.get_some_layers_at_index_as_list(layer_descr_list, latitude_index, longitude_index)

    def get_all_layers_at_location_as_list(self, location):
        """
        Returns a list containing the value of each layer at the specified location. The list is ordered according to
        the original `layer_descr_list`.
        """
        return self.get_some_layers_at_location_as_list(self._layer_descr_list, location)

    def get_all_layers_at_location_as_dict(self, location):
        """
        Returns a dictionary containing the value of each layer at the specified location. The keys of the dictionary
        are taken from the original `layer_descr_list`.
        """
        some_layer = self._layers.values()[0]
        (latitude_index, longitude_index) = some_layer.get_indices_from_location(location)
        return self.get_all_layers_at_index_as_dict(latitude_index, longitude_index)

    def set_some_layers_at_index_from_list(self, layer_descr_list, latitude_index, longitude_index, list_of_values):
        """
        Sets the value of each layer at the specified location. The list is assumed to be ordered according to the
        original `layer_descr_list`.

        See also: :meth:`set_all_layers_at_index_as_list`, :meth:`get_all_layers_at_index_from_list`, \
                    :meth:`get_some_layers_at_index_from_list`
        """
        if len(list_of_values) is not len(layer_descr_list):
            raise ValueError("Could not set values: expected %d values but got %d." % (len(self._layer_descr_list),
                                                                                     len(list_of_values)))

        dict_of_values = {}
        for (descr, value) in zip(layer_descr_list, list_of_values):
            dict_of_values[descr] = value
        self.set_layers_at_index_from_dict(latitude_index, longitude_index, dict_of_values)

    def set_all_layers_at_index_from_list(self, latitude_index, longitude_index, list_of_values):
        """
        Sets the value of each layer at the specified location. The list is assumed to be ordered according to the
        original `layer_descr_list`.

        See also: :meth:`set_some_layers_at_index_as_list`, :meth:`get_all_layers_at_index_from_list` \
                    :meth:`get_some_layers_at_index_from_list`
        """
        self.set_some_layers_at_index_from_list(self._layer_descr_list, latitude_index, longitude_index, list_of_values)

    def set_layers_at_index_from_dict(self, latitude_index, longitude_index, dict_of_values):
        """
        Sets the value of the layers at the specified location. The keys of the dictionary must correspond to the
        original `layer_descr_list`.

        See also: :meth:`set_all_layers_at_index_as_list`, :meth:`set_some_layers_at_index_as_list`, \
                    :meth:`get_all_layers_at_index_from_dict`.
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

        destination_data_map = DataMap2D.from_existing_DataMap2D(list_of_layers[0], 0)

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

    def combine_values_elementwise_across_layers_using_function(self, combination_function, layer_descr_list=None):
        """
        Combines all of the values in the specified layers elementwise into a new :class:`DataMap2D` according to
        ``combination_function``. Values which are not set (i.e. ``combination_function`` returns None) will be NaN.

        Does not modify any existing data.

        ``combination_function`` should have the following signature::

            def combination_function(latitude, longitude, latitude_index, longitude_index, list_of_values_in_order):
                # The list will be ordered according to 'layer_descr_list' (original list will be used if None provided)
                ...
                return combined_value_for_pixel      # may also return None to keep NaN value

        :param combination_function: function used to update the values
        :type combination_function: function object
        :param layer_descr_list: list of layer descriptions that will be combined
        :return: data map holding the combined values
        :rtype: :class:`DataMap2D`
        """
        layer_descr_list = layer_descr_list or self._layer_descr_list
        if len(layer_descr_list) == 0:
            raise ValueError("Could not combine layers: no layer")
        elif len(layer_descr_list) == 1:
            raise ValueError("Could not combine layers: only one layer")

        sample_datamap = self.get_layer(layer_descr_list[0])
        destination_datamap = DataMap2D.get_copy_of(sample_datamap)
        destination_datamap.reset_all_values(fill_value=numpy.NaN)

        def pixel_update_function(latitude, longitude, latitude_index, longitude_index, current_value):
            all_values = self.get_some_layers_at_index_as_list(layer_descr_list, latitude_index, longitude_index)
            return combination_function(latitude, longitude, latitude_index, longitude_index, all_values)

        destination_datamap.update_all_values_via_function(pixel_update_function, verbose=False)

        return destination_datamap

    def reset_all_values(self, fill_value=numpy.NaN):
        """
        Resets all values of all layers to `fill_value`.
        """
        for layer in self._layers.values():
            layer.reset_all_values(fill_value)

    def to_pickle(self, filename):
        """
        Save the DataMap3D to a pickle with the specified ``filename``. See also: :meth:`from_pickle`.

        :param filename: destination filename
        :type filename: str
        :return: None
        """
        with open(filename, "w") as f:
            pickle.dump(self, f)

    @classmethod
    def from_pickle(cls, filename):
        """
        Loads the DataMap3D from a pickle with the specified ``filename``. See also: :meth:`to_pickle`.

        :param filename: destination filename
        :type filename: str
        :return:
        :rtype: :class:`DataMap3D`
        """
        with open(filename, "r") as f:
            return pickle.load(f)

    # Helper functions required for pickling
    # Objects with open file descriptors (e.g. logs) cannot be pickled, so we remove the logs when saving
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['log']
        return state

    def __setstate__(self, d):
        self.__dict__.update(d)

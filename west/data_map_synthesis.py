from data_map import DataMap2D, DataMap3D
import numpy


def _raise_error_if_not_correct_type(obj, expected_type):
    """Raises a TypeError if ``obj`` is not of the ``expected_type``."""
    if not isinstance(obj, expected_type):
        raise TypeError("Expected %r to be of type %r but got %r." % (obj,
                                                                      expected_type, obj.__class__))


def _raise_error_if_bad_input(tuple_of_datamaps, expected_type):
    """
    Raises the appropriate error if the input to a synthesize_pixels*
    function is invalid.
    """
    if not isinstance(tuple_of_datamaps, tuple):
        raise TypeError("Expected a tuple of DataMaps as an argument; got %r "
                        "instead." % tuple_of_datamaps)

    if not len(tuple_of_datamaps):
        raise ValueError("Expected to receive at least one input DataMap")

    arbitrary_datamap = tuple_of_datamaps[0]
    for input_datamap in tuple_of_datamaps:
        _raise_error_if_not_correct_type(input_datamap, expected_type)
        arbitrary_datamap.raise_error_if_datamaps_are_incomparable(input_datamap)


def synthesize_pixels(combination_function, tuple_of_datamap2ds):
    """
        Creates a new :class:`data_map.DataMap2D`, iterates over all of its
        pixels, and fills each pixel independently and according to the output
        of ``combination_function``. The new data map is returned.

        At each pixel, ``combination_function``
        will receive a tuple of values corresponding to the value of each
        input DataMap2D at that location. For example,
        if ``tuple_of_datamap2ds = (dm_a, dm_b)``, then ``tuple_of_values``
        is equivalent to::

            (dm_a.get_value_by_index(...), dm_b.get_value_by_index(...))

        Order will always be preserved.

        ``combination_function`` should have the following signature::

            def combination_function(latitude, longitude, latitude_index,
                                     longitude_index, tuple_of_values):
                # The order of the tuple will be that of the tuple_of_datamap2ds

                ...
                return value_for_synthesized_pixel
                # may also return None if the default NaN value is desired

        Example usage::

            signal = ...
            bandwidth = ...
            is_whitespace_datamap2d = ...
            noise_datamap2d = ...

            # Function to calculate the ideal data rate at a pixel
            def ideal_data_rate(latitude, longitude, latitude_index,
                                longitude_index, tuple_of_values):
                is_whitespace, noise_level = tuple_of_values
                if not is_whitespace:
                    return 0
                else:
                    return bandwidth * log(1 + signal / noise_level)

            # Calculate the rate map for a single channel
            rate_map = synthesize_pixels(ideal_data_rate,
                                         (is_whitespace_datamap2d,
                                          noise_datamap2d))
    """
    _raise_error_if_bad_input(tuple_of_datamap2ds, DataMap2D)

    arbitrary_input_datamap = tuple_of_datamap2ds[0]
    output_map = arbitrary_input_datamap.get_clean_copy(fill_value=numpy.nan)

    def calculation_function(latitude, longitude, latitude_index,
                             longitude_index, current_value):
        tuple_of_values = (datamap.get_value_by_index(latitude_index,
                                                      longitude_index) for
                           datamap in tuple_of_datamap2ds)
        return combination_function(latitude, longitude, latitude_index,
                                    longitude_index, tuple_of_values)

    output_map.update_all_values_via_function(calculation_function)
    return output_map


def synthesize_pixels_all_layers(combination_function, tuple_of_datamap3ds):
    """
    See :meth:`synthesize_pixels` for the main documentation of this
    function.

    This function differs from :meth:`synthesize_pixels` in that it operates
    on :class:`data_map.DataMap3D` objects. At each pixel, a list of values
    (rather than a scalar value) is returned, with each element corresponding to
    a layer in the DataMap3D.

    .. warning:: Although this function will enforce that all of the DataMap3D \
    objects have the same set of layers, it does not enforce (although it \
    assumes) that they are in the same order. Behavior is undefined if layer \
    order is not consistent.
    """
    _raise_error_if_bad_input(tuple_of_datamap3ds, DataMap3D)

    arbitrary_input_datamap3d = tuple_of_datamap3ds[0]
    output_map = arbitrary_input_datamap3d.get_clean_copy(fill_value=numpy.nan)

    arbitrary_input_datamap2d = arbitrary_input_datamap3d.get_arbitrary_layer()
    for (lat_idx, lat) in enumerate(arbitrary_input_datamap2d.latitudes):
        for (lon_idx, lon) in enumerate(arbitrary_input_datamap2d.longitudes):
            tuple_of_values = (datamap.get_all_layers_at_index_as_list(
                lat_idx, lon_idx) for datamap in tuple_of_datamap3ds)

            new_values = combination_function(lat, lon, lat_idx, lon_idx,
                                              tuple_of_values)
            # The "do not set if None" behavior is captured in this function
            output_map.set_all_layers_at_index_from_list(lat_idx, lon_idx,
                                                         new_values)

    return output_map

from data_map import DataMap2D
import numpy



def calculate_cdf_from_map(data_map, weight_map=None, mask_map=None):
    """
    Calculate a CDF of a data map given a corresponding (optional) weight map. If no weight map is given, equal weights
    will be used.

    A mask may be provided. Locations which are zero will not be included in the CDF.

    .. note:: Implementation is provided by `calculate_cdf_from_matrices`. This function is merely a convenient wrapper.

    :param data_map:
    :type data_map: :class:`data_map.DataMap2D`
    :param weight_map:
    :type weight_map: :class:`data_map.DataMap2D`
    :param mask_map:
    :type mask_map: :class:`data_map.DataMap2D`
    :return: cdfX, cdfY, average, median
    """
    # Check data types
    if not isinstance(data_map, DataMap2D):
        raise TypeError("Data map must be a DataMap2D.")
    if weight_map is not None and not isinstance(weight_map, DataMap2D):
        raise TypeError("Weight map must be a DataMap2D.")
    if mask_map is not None and not isinstance(mask_map, DataMap2D):
        raise TypeError("is_in_region map must be a DataMap2D.")

    if weight_map is not None:
        data_map.raise_error_if_data_maps_are_incomparable(weight_map)
    if mask_map is not None:
        data_map.raise_error_if_data_maps_are_incomparable(mask_map)

    data_matrix = data_map.get_matrix_copy()
    if weight_map is None:
        weight_matrix = None
    else:
        weight_matrix = weight_map.get_matrix_copy()
    if mask_map is None:
        mask_matrix = None
    else:
        mask_matrix = mask_map.get_matrix_copy()

    return calculate_cdf_from_matrices(data_matrix, weight_matrix, mask_matrix)


def calculate_cdf_from_matrices(data_matrix, weight_matrix=None, mask_matrix=None):
    """
    Calculate a CDF of a data matrix given a corresponding (optional) weight map. If no weight map is given, equal
    weights will be used.

    A mask may be provided. Elements which are zero will not be included in the CDF.

    :param data_matrix:
    :type data_matrix: :class:`numpy.matrix`
    :param weight_matrix:
    :type weight_matrix: :class:`numpy.matrix`
    :param mask_matrix:
    :type mask_matrix: :class:`numpy.matrix`
    :return: cdfX, cdfY, average, median
    """
    if weight_matrix is None:
        weight_matrix = numpy.ones(numpy.shape(data_matrix))

    if mask_matrix is None:
        mask_matrix = numpy.ones(numpy.shape(data_matrix))

    # With numpy, 0 = included after masking and 1 = masked, so flip this
    mask_matrix = numpy.logical_not(mask_matrix)

    data_matrix_masked = numpy.ma.masked_array(data_matrix.astype(float), mask=mask_matrix)
    weight_matrix_masked = numpy.ma.masked_array(weight_matrix.astype(float), mask=mask_matrix)

    data_array = data_matrix_masked.compressed()     # 1-D base array after removing masked elements
    if hasattr(data_array, "A1"):
        data_array = data_array.A1
    weight_array = weight_matrix_masked.compressed()
    if hasattr(weight_array, "A1"):
        weight_array = weight_array.A1

    bad_indices = numpy.logical_or(numpy.isnan(data_array), numpy.isnan(weight_array))
    bad_indices = numpy.logical_or(bad_indices, numpy.isinf(data_array))
    bad_indices = numpy.logical_or(bad_indices, numpy.isinf(weight_array))
    data_array[bad_indices] = 0
    weight_array[bad_indices] = 0

    order = data_array.argsort()

    sorted_data_array = data_array[order]
    sorted_weight_array = weight_array[order]

    summed_weight_array = numpy.cumsum(sorted_weight_array)

    cdfX = sorted_data_array
    cdfY = summed_weight_array / sum(sorted_weight_array)

    # Find the first element in cdfY which is greater than 0.5
    # The corresponding cdfX value will be the median
    # median_index = numpy.where(cdfY >= 0.5)[0][0]
    median_index = numpy.argmax(cdfY >= 0.5)
    median = cdfX[median_index]

    average = numpy.average(sorted_data_array, weights=sorted_weight_array)

    return cdfX, cdfY, average, median

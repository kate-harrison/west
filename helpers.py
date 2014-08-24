
horizontal_separator = "".center(80, "-")



# Source: http://stackoverflow.com/questions/695794/more-efficient-way-to-pickle-a-string

# def pickle(fname, obj):
#     import cPickle, gzip
#     cPickle.dump(obj=obj, file=gzip.open(fname, "wb", compresslevel=3), protocol=2)
#
# def unpickle(fname):
#     import cPickle, gzip
#     return cPickle.load(gzip.open(fname, "rb"))



def get_cochannel_and_first_adjacent(region, channel):
    affected_channels = [channel]
    for adj_chan in [channel-1, channel+1]:
        if channels_are_adjacent_in_frequency(region, adj_chan, channel):
            affected_channels.append(adj_chan)
    return affected_channels

def channels_are_adjacent_in_frequency(region, chan1, chan2):
    try:
        (low1, high1) = region.get_frequency_bounds(chan1)
        (low2, high2) = region.get_frequency_bounds(chan2)
        return abs(low1 - high2) < .001 or abs(low2 - high1) < .001
    except ValueError:
        # If the channel is undefined for the region, it will return a ValueError. In that case,
        # the channels are defined as not being adjacent.
        return False


def add_bounding_box_to_kml(kml, bounding_box):
    poly = kml.newpolygon()

    poly.outerboundaryis.coords = [
        (bounding_box['max_lon'], bounding_box['max_lat']),
        (bounding_box['min_lon'], bounding_box['max_lat']),
        (bounding_box['min_lon'], bounding_box['min_lat']),
        (bounding_box['max_lon'], bounding_box['min_lat']),
        (bounding_box['max_lon'], bounding_box['max_lat'])      # repeat the last one for closure
    ]

    return poly

def lists_are_almost_equal(array1, array2, tolerance=1e-4):
    """
    Returns True if corresponding elements differ by no more than the tolerance. Returns False otherwise.
    """
    return all([abs(element1 - element2) < tolerance for element1, element2 in zip(array1, array2)])

def find_first_index_where(list_to_search, is_found_function):
    """
    Returns the first index where ``is_found_function(value)`` is True.

    :param list_to_search: list of items to search (in order)
    :type list_to_search: list
    :param is_found_function: function which operates on a single element and outputs True if the desired condition \
            is met
    :type is_found_function: function object
    :return: index if condition is met; otherwise, None
    :rtype: int or None
    """
    try:
        first_index = next(index for index, value in enumerate(list_to_search) if is_found_function(value))
    except StopIteration:
        return None

    return first_index

def find_first_value_above_or_equal(list_to_search, value_to_find):
    """
    Returns the first index where the ``list_to_search[index] >= value_to_find``. Returns None if no such index
    exists.
    """
    return find_first_index_where(list_to_search, lambda v: v > value_to_find)

def find_last_value_below_or_equal(list_to_search, value_to_find):
    """
    Returns the last index where the ``list_to_search[index] <= value_to_find``. Returns None if no such index
    exists.
    """
    index = find_first_value_above_or_equal(list_to_search, value_to_find)

    # Equality is fine
    if index is not None and abs(list_to_search[index] - value_to_find) < 0.001:
        return index

    # Otherwise need to subtract 1
    if index is not None and index > 0:
        return index - 1

    # Not found
    return None

def find_first_value_approximately_equal(list_to_search, value_to_find, tolerance=1e-4):
    """
    Returns the first index such that ``abs(list_to_search[index] - value_to_find) < tolerance``. Returns None if no
    such index exists.
    """
    return find_first_index_where(list_to_search, lambda v: abs(value_to_find - v) < tolerance)

def generate_submap_for_protected_entity(base_datamap2d, protected_entity):
    bb = protected_entity.get_bounding_box()
    latitude_bounds = (bb['min_lat'], bb['max_lat'])
    longitude_bounds = (bb['min_lon'], bb['max_lon'])

    return base_datamap2d.generate_submap(latitude_bounds, longitude_bounds,
                                          generate_even_if_submap_partially_outside_datamap=True)

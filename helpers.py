
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


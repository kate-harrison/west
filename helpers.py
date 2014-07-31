from math import pi, sin, cos, atan2, sqrt, asin



horizontal_separator = "".center(80, "-")



earth_radius_km = 6371   # Earth's mean radius

# Source: http://www.movable-type.co.uk/scripts/latlong.html
def latlong_to_km(location1, location2):
    lat1, long1 = [l * pi/180 for l in location1]
    lat2, long2 = [l * pi/180 for l in location2]

    d_lat = (lat2 - lat1)
    d_long = (long2 - long1)
    a = sin(d_lat/2) ** 2 + cos(lat1) * cos(lat2) * sin(d_long/2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return earth_radius_km * c

# Source: http://www.movable-type.co.uk/scripts/latlong.html
def km_to_latlong(location, dist, dir):
    """Finds the latitude and longitude (in degrees) coordinates
    of the point *dist* km away from (*lat1*, *long1*) (in degrees) in
    direction *dir* clockwise from North (in degrees)"""
    lat1, long1 = [l * pi/180 for l in location]

    dir = dir * pi/180


    lat2 = asin( sin(lat1)*cos(dist/earth_radius_km) + cos(lat1)*sin(dist/earth_radius_km)*cos(dir) )
    long2 = long1 + atan2( sin(dir)*sin(dist/earth_radius_km)*cos(lat1), cos(dist/earth_radius_km)-sin(lat1)*sin(lat2) )

    lat2 = lat2 * 180/pi
    long2 = long2 * 180/pi
    return lat2, long2






# Source: http://geospatialpython.com/2011/08/point-in-polygon-2-on-line.html

# Improved point in polygon test which includes edge
# and vertex points

def point_in_poly(x,y,poly):

    # check if point is a vertex
    if (x,y) in poly: return "IN"

    # check if point is on a boundary
    for i in range(len(poly)):
        p1 = None
        p2 = None
        if i==0:
            p1 = poly[0]
            p2 = poly[1]
        else:
            p1 = poly[i-1]
            p2 = poly[i]
        if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
            return "IN"

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    if inside: return "IN"
    else: return "OUT"




# def latlon_in_bounding_box(lat, lon, bb):
#     return (bb['min_lat'] <= lat <= bb['max_lat']) and (bb['min_lon'] <= lon <= bb['max_lon'])
def location_in_bounding_box(location, bb):
    (lat, lon) = location
    return (bb['min_lat'] <= lat <= bb['max_lat']) and (bb['min_lon'] <= lon <= bb['max_lon'])






# # Test a vertex for inclusion
# poligono = [(-33.416032,-70.593016), (-33.415370,-70.589604),
#             (-33.417340,-70.589046), (-33.417949,-70.592351),
#             (-33.416032,-70.593016)]
# lat= -33.416032
# lon= -70.593016
#
# print point_in_poly(lat, lon, poligono)
#
# # test a boundary point for inclusion
# poly2 = [(1,1), (5,1), (5,5), (1,5), (1,1)]
# x = 3
# y = 1
# print point_in_poly(x, y, poly2)




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
    (low1, high1) = region.get_frequency_bounds(chan1)
    (low2, high2) = region.get_frequency_bounds(chan2)
    # If the channel is undefined for the region, we will return False
    if any([bound is None for bound in [low1, low2, high1, high2]]):
        return False
    return (low1 == high2) or (low2 == high1)

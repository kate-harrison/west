# import boundary
# import random
# import simplekml
#
# #b = boundary.BoundaryContinentalUnitedStates(None)
# b = boundary.BoundaryContinentalUnitedStates(None)
# # kml = b.export_to_kml(save=False)
#
# kml = simplekml.Kml()
#
#
#
#
#
# for test_num in range(5000):
#     print test_num
#     rand_lat = random.randrange(27,50)
#     rand_lon = random.randrange(-130, -60)
#     point_in_polygon = b.location_inside_boundary( (rand_lat, rand_lon) )
#
#     point = kml.newpoint(name='A Point')
#     point.coords = [(rand_lon, rand_lat)]
#     if point_in_polygon:
#         point.style.labelstyle.color = simplekml.Color.blue
#     else:
#         point.style.labelstyle.color = simplekml.Color.red
#
# kml.save("multitest.kml")
#
#
# print "MTV in polygon? ", b.location_inside_boundary( (41, -121) )






import boundary
import data_storage
import pickle

#             return (24.5 <= lat <= 49.38) and (-124.77 <= lon <= -66)

latitude_bounds = [24.5, 49.38]
longitude_bounds = [-124.77, -66]
num_latitude_divisions = 200
num_longitude_divisions = 300

grid = data_storage.DataPointGrid.from_grid_specification(latitude_bounds, longitude_bounds,
                                                          num_latitude_divisions, num_longitude_divisions)


# test_obj ="Hi there"









b = boundary.BoundaryContinentalUnitedStates(None)

for lat_index in range(num_latitude_divisions):
    print(lat_index)
    for lon_index in range(num_longitude_divisions):
        location = (grid.get_latitude_by_index(lat_index), grid.get_longitude_by_index(lon_index))
        inside = b.location_inside_boundary(location)
        grid.set_value_by_index(lat_index, lon_index, inside)


with open("is_in_region200x300.pcl", "w") as f:
    pickle.dump(grid, f)


map = grid.make_map()
map.blocking_show()


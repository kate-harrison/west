# import data_map
#
# dpg = data_map.DataMap2D.from_grid_specification([-3, 2], [-4, 5], 2, 3)
#
# print("Initial matrix:")
# print(dpg.mutable_matrix)
#
#
# dpg.set_value_by_location( (-3, -4), 5)
#
# print("Matrix after setting first element to 5:")
# print(dpg.mutable_matrix)
#
# print("Value of first element: %f" % dpg.mutable_matrix[0,0])
#
#
#
#
#
# #############################
#
# dpg1 = data_map.DataMap2D.from_grid_specification( [0, 5], [0, 5], 5, 5)
# dpg1.set_value_by_index(0,0,5)
#
# dpg2 = data_map.DataMap2D.from_grid_specification( [0, 5], [0, 5], 5, 5)
# dpg2.set_value_by_index(0,0,.5)
#
# print("Matrix 1:\n", dpg1.mutable_matrix)
# print("Matrix 2:\n", dpg2.mutable_matrix)
#
# def test_function(a, b):
#     #return a * b
#     return max(a,b)
#
# new_dpg = dpg1.combine_grids(dpg2, test_function)
# print("Output matrix:\n", new_dpg.mutable_matrix)
#
#
#
# #new_dpg[:] = 5
# #new_dpg[1,1] = 2
#
# new_dpg.reset_all_values(5)
# new_dpg.set_value_by_index(1,1,2)
#
# print("Planning to plot this matrix:")
# print(new_dpg.mutable_matrix)
#
# new_dpg.make_map()

import pickle
import simplekml

with open("is_in_region200x300.pcl", "r") as f:
    grid = pickle.load(f)


def poly_transformation_function(poly, value):
    if value:
        # poly.style.polystyle.color = simplekml.Color.blue # simplekml.Color.changealphaint(.5, simplekml.Color.blue)
        poly.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.blue)

    else:
        # poly.style.polystyle.color = simplekml.Color.changealphaint(.5, simplekml.Color.red)
        poly.style.polystyle.color = simplekml.Color.changealphaint(0, simplekml.Color.green)


def include_polygon_function(value):
    return bool(value)


grid.export_to_kml("is_in_region200x300.kml", geometry_modification_function=poly_transformation_function, include_polygon_function=include_polygon_function)

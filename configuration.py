import os

# TODO: find a better way of organizing configuration parameters

package_directory, _ = os.path.split(__file__)
base_data_directory = os.path.join(package_directory, "data")
region_directory_name = "Region"
boundaries_directory_name = "Boundaries"
protected_entities_directory_name = "ProtectedEntities"


def add_paths_for_region(region_name):
    paths[region_name] = {}
    region_base_dir = os.path.join(base_data_directory, region_directory_name, region_name)
    paths[region_name]['base'] = region_base_dir
    paths[region_name]['boundaries'] = os.path.join(region_base_dir, boundaries_directory_name)
    paths[region_name]['protected_entities'] = os.path.join(region_base_dir, protected_entities_directory_name)


paths = {}
add_paths_for_region("UnitedStates")

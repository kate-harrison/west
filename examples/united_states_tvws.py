# This code sample demonstrates how to generate and plot data representing TV
# white space availability in the United States.

from west.data_management import *
from west.data_map import *
from west.boundary import BoundaryContinentalUnitedStates, \
    BoundaryContinentalUnitedStatesWithStateBoundaries
from west.region_united_states import RegionUnitedStates
from west.ruleset_fcc2012 import RulesetFcc2012
from west.device import Device

# Specify the type of device
test_device = Device(is_portable=False, haat_meters=30)

# The data will be on a 200x300 lat-long grid. The first argument specifies
# the lat-long boundaries of this grid. In this case, those boundaries are:
#   [24.5, 49.38] degrees latitude
#   [-124.77, -66] degrees longitude
# These values can be see in the definition of
# DataMap2DContinentalUnitedStates in west.data_map and can be altered by
# subclassing DataMap2DWithFixedBoundingBox in that module.
datamap_spec = SpecificationDataMap(DataMap2DContinentalUnitedStates, 200, 300)

# Data will only be computed for locations inside the continental United States.
region_map_spec = SpecificationRegionMap(BoundaryContinentalUnitedStates,
                                         datamap_spec)

# Whitespace will be computed using the values above, protected entities
# defined in RegionUnitedStates, and the ruleset defined in RulesetFcc2012.
is_whitespace_map_spec = SpecificationWhitespaceMap(region_map_spec,
                                                    RegionUnitedStates,
                                                    RulesetFcc2012, test_device)

# Generate the TVWS availability data if it does not already exist;
# otherwise, the data is loaded from disk. The data is in the form of a
# DataMap3D with each layer representing the whitespace availability on a
# particular TV channel. A value of '1' indicates that whitespace is
# available at that location; '0' means WS is not available.
is_whitespace_map = is_whitespace_map_spec.fetch_data()

# Turn the DataMap3D into a DataMap2D by summing all layers at each location.
total_whitespace_channels = is_whitespace_map.sum_all_layers()

# Fetch (generate or load) a region map which will be used to mask the
# DataMap2D in order to create a white background in the image and the
# appearance of a "floating" map.
is_in_region_map = region_map_spec.fetch_data()

# Plot the data
plot = total_whitespace_channels.make_map(is_in_region_map=is_in_region_map)

# Add outlines of the individual states and customize their appearance.
plot.add_boundary_outlines(
    boundary=BoundaryContinentalUnitedStatesWithStateBoundaries())
plot.set_boundary_color('k')
plot.set_boundary_linewidth('1')

# Save the plot
plot.save("Number of TVWS channels in the United States.png")

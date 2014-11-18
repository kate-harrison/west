# This code sample demonstrates how to generate and plot whitespace capacity
# in the United States. Note that it uses FAKE data for the noise floor. The
# main purpose of this code sample is to demonstrate how to combine multiple
# pieces of data (e.g. noise floor and whitespace availability) on a
# pixel-by-pixel basis.

from west.data_map_synthesis import *
from west.data_management import *
from west.data_map import *
from west.boundary import BoundaryContinentalUnitedStates
from west.region_united_states import RegionUnitedStates
from west.ruleset_fcc2012 import RulesetFcc2012
from west.device import Device
from numpy import log, random

# Specify the device type
test_device = Device(is_portable=False, haat_meters=30)

# Specify the starting data
datamap_spec = SpecificationDataMap(DataMap2DContinentalUnitedStates, 200, 300)
region_map_spec = SpecificationRegionMap(BoundaryContinentalUnitedStates,
                                         datamap_spec)
is_whitespace_map_spec = SpecificationWhitespaceMap(region_map_spec,
                                                    RegionUnitedStates,
                                                    RulesetFcc2012, test_device)

# Fetch (generate or load) the starting data
is_in_region_map = region_map_spec.fetch_data()
is_whitespace_map = is_whitespace_map_spec.fetch_data()

# We will focus on a single TV channel
is_whitespace_channel25 = is_whitespace_map.get_layer(25)

# Generate a map of the noise floor (e.g. from TV stations or other white
# space devices). Here we use FAKE data.
#
# Note: this is a common place to add customization. Rather than (or in
# addition to) loading data about the noise floor, one may with to load e.g.
# population or economic data.
noise_layer = is_in_region_map.get_clean_copy()
noise_layer.mutable_matrix = random.rand(200, 300) / 1e6

# Define a function that takes data about a single lat-long location ("pixel")
# and returns the desired value for that location. This function will be used
# later with the iterator method synthesize_pixels().
def per_pixel_data_rate(latitude, longitude, latitude_index, longitude_index,
                        tuple_of_values):
    # In this case, the function will receive the values of
    # is_whitespace_channel25 and noise_layer at this location. These are
    # packed into the variable tuple_of_values but are unpacked with the
    # following line:
    is_whitespace, noise_level = tuple_of_values

    # We use a FAKE signal level for demonstration purposes.
    signal = 1e-5

    # We define the bandwidth here. In other cases, the user may wish to load
    # this value from the Region object on a per-channel basis.
    bandwidth = 6e6

    # The data rate is necessarily zero if the channel is unavailable for
    # white space use.
    if not is_whitespace:
        return 0
    # Otherwise, we calculate the Shannon capacity in Mbps given the input data.
    else:
        return bandwidth * log(1 + signal / noise_level) / 1e6

# Calculate the data rate using the per-pixel function defined above.
#
# Notice that the data in tuple_of_values (input to per_pixel_data_rate()) is
# defined by the second argument to synthesize_pixels().
rate_map = synthesize_pixels(per_pixel_data_rate, (is_whitespace_channel25,
                                               noise_layer))

# Add a title and colorbar
# plot.add_colorbar(vmin=0, vmax=50, label="Channels")

# Plot and save the resulting data
plot = rate_map.make_map(is_in_region_map=is_in_region_map)
plot.set_title("Example data rates on channel 25")
plot.add_colorbar(vmin=0, vmax=50, label="Data rate (Mbps)",
                  decimal_precision=1)
plot.save("Example data rate map for the United States.png")




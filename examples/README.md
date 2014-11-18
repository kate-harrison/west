Overview
--------
These examples are meant to help users learn about WEST and quickly accomplish
their goals. Please email me with any comments and suggestions.

**As with all code which uses WEST, please run these examples from a directory 
*outside* of the repository.**


Evaluating white space availability in the United States
--------------------------------------------------------
Please see
[```united_states_tvws.py```](https://github.com/kate-harrison/west/blob/master/examples/united_states_tvws.py).
This example demonstrates how to load and plot the white space availability 
in the United States.


Evaluating white space capacity in the United States
----------------------------------------------------
Please see
[```united_states_data_rates.py```](https://github.com/kate-harrison/west/blob/master/examples/united_states_data_rates.py).
Note that this can be easily extended to utilize a user-provided model for 
data rates.


Combining white space availability data with other data (population, economic, etc.)
------------------------------------------------------------------------------------
Please see
[```united_states_data_rates.py```](https://github.com/kate-harrison/west/blob/master/examples/united_states_data_rates.py).
The techniques used in this example work just as well with other types of data.


Evaluating white space availability in other regions
----------------------------------------------------
The examples for the United States can be easily extended to work for other 
regions. Below is a list of necessary modifications:

1. Subclass
[```west.protected_entity.ProtectedEntity```](https://github.com/kate-harrison/west/blob/master/west/protected_entity.py)
as needed to define 
each of the entities which is protected in the target region. Consider using 
[```west.protected_entity_tv_station.ProtectedEntityTVStation```](https://github.com/kate-harrison/west/blob/master/west/protected_entity_tv_station.py)
as an example.
2. Subclass
[```west.protected_entities.ProtectedEntities```](https://github.com/kate-harrison/west/blob/master/west/protected_entities.py)
as needed to load
 data about the target region's protected entities and create 
 ```ProtectedEntity``` objects. Users are strongly encouraged to use 
[```west.protected_entities_plmrs```](https://github.com/kate-harrison/west/blob/master/west/protected_entities_plmrs.py)
and
[```west.protected_entities_tv_stations```](https://github.com/kate-harrison/west/blob/master/west/protected_entities_tv_stations.py)
as examples.
3. Subclass
[```west.region.Region```](https://github.com/kate-harrison/west/blob/master/west/region.py).
This class will contain region-specific
data such as which TV channels are available for white space use, 
the width of each channel, and the set of protected entities. Users are 
encouraged to use
[```west.region.region_united_states.RegionUnitedStates```](https://github.com/kate-harrison/west/blob/master/west/region_united_states.py) 
as an exmaple.
4. If necessary, subclass
[```west.ruleset.Ruleset```](https://github.com/kate-harrison/west/blob/master/west/ruleset.py)
to specify a new ruleset.
5. Use these new classes with the US-centric examples, 
replacing references to classes as necessary. The interfaces have been 
designed to allow as much flexibility as possible.

Users are encouraged to subclass from existing subclasses (e.g.
[```west.ruleset_fcc2012.RulesetFcc2012```](https://github.com/kate-harrison/west/blob/master/west/ruleset_fcc2012.py)
) and make only necessary changes when practical. However, 
stability of code is never guaranteed.

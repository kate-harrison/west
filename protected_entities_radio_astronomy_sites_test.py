from protected_entities_radio_astronomy_sites import ProtectedEntitiesRadioAstronomySitesUnitedStates
from region_united_states import RegionUnitedStates

simulation = None
region = RegionUnitedStates(simulation)
# pe = ProtectedEntitiesRadioAstronomySitesUnitedStates(simulation, region)




# import simplekml, helpers
# ras_kml = simplekml.Kml()
# ras_bb_kml = simplekml.Kml()
#
# for entity in self.get_list_of_entities_on_channel(ras_channel):
#     print entity.to_string()
#     entity.add_to_kml(ras_kml)
#     bb = entity.get_bounding_box()
#     helpers.add_bounding_box_to_kml(ras_bb_kml, bb)
#
# ras_kml.save("RAS.kml")
# ras_bb_kml.save("RAS_BB.kml")

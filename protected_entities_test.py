from protected_entities_tv_stations import ProtectedEntitiesTVStationsUnitedStatesFromGoogle
from protected_entities_plmrs import ProtectedEntitiesPLMRSUnitedStatesFromGoogle


PE = ProtectedEntitiesTVStationsUnitedStatesFromGoogle(None)

# PE.export_to_kml("tv_towers.kml")
# PE.export_to_kml("digital_tv_towers.kml", filter_fcn=lambda x: x.is_digital())



PE_PLMRS = ProtectedEntitiesPLMRSUnitedStatesFromGoogle(None)

PE_PLMRS.export_to_kml("all_plmrs.kml")
PE_PLMRS.export_to_kml("metro_plmrs.kml", filter_fcn=lambda x: x.is_metro())

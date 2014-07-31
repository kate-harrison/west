from protected_entity_tv_station import ProtectedEntityTVStation

simulation = None
latitude = None
longitude = -143
channel = 5
ERP_Watts = 15
HAAT_meters = 10
tx_type = "DA"

print("***This should produce an error:")
tv = ProtectedEntityTVStation(simulation, latitude, longitude, channel, ERP_Watts,
           HAAT_meters, tx_type)

print("***This should not produce an error:")
latitude = 40
tv = ProtectedEntityTVStation(simulation, latitude, longitude, channel, ERP_Watts,
               HAAT_meters, tx_type)

from protected_entity_tv_station import ProtectedEntityTVStation

container = None    # will cause error
latitude = None
longitude = -143
channel = 5
ERP_Watts = 15
HAAT_meters = 10
tx_type = "DA"

print("***This should produce an error:")
tv = ProtectedEntityTVStation(container, latitude, longitude, channel, ERP_Watts,
           HAAT_meters, tx_type)

print("***This should not produce an error:")
latitude = 40
tv = ProtectedEntityTVStation(container, latitude, longitude, channel, ERP_Watts,
               HAAT_meters, tx_type)

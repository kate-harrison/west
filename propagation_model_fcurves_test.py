
#
# from ctypes import *
#
#
# #cdll.LoadLibrary("libc.dylib")
# #libc = CDLL("libc.dylib")
#
#
# cdll.LoadLibrary("curves_subroutines.so")
# clib = CDLL("curves_subroutines.so")
#
# # Holy smokes this works!!
# #print clib.length_('testy  asdf ', 6)
#
#
# erp = c_float(10.5)    # kW
# haat = c_float(30)   # meters
# channel = c_long(9)     # FM or TV channel number
# field_strength_dbu = c_float(-1)   # input or output, depending on switch
# distance = c_float(100)  # km    # input or output, depending on switch
# switch = c_long(1)      # 1 = compute field strength from distance
# # 2 = compute distance from field strength
# curve = c_long(0)       # 0 = F(50,50)
# # 1 = F(50,10)
# flag = c_byte()     # error code ("  " is a normal return)
#
# #func = clib.tvfmfs_metric__(erp, haat, channel, field_strength_dbu, distance, switch, curve, flag)
# #func.restype =
# func = clib.tvfmfs_metric__
#
# # Source: http://snfactory.in2p3.fr/soft/snifs/IFU_C_iolibs/f2c_8h.html
# #typedef float real
# #typedef double 	doublereal
# #typedef long int 	integer
# #typedef long int 	ftnlen
#
# # http://python.net/crew/theller/ctypes/tutorial.html#fundamental-data-types
#
#
# #/* Subroutine */ int tvfmfs_metric__(real *erp, real *haat, integer *channel,
# #	real *field, real *distance, integer *switch__, integer *curve, char *
# #	flag__, ftnlen flag_len)
#
#
# # real* -> float* -> POINTER(c_float)
# # integer* -> long int * -> POINTER(c_long)
# # char * -> POINTER(c_byte) or c_char_p ??
# # ftnlen -> long int -> c_long
#
# func.restype = c_int
# func.argtypes = [POINTER(c_float), POINTER(c_float), POINTER(c_long),
#                  POINTER(c_float), POINTER(c_float), POINTER(c_long), POINTER(c_long), POINTER(c_byte), c_long]
# print func( byref(erp), byref(haat), byref(channel), byref(field_strength_dbu), byref(distance), byref(switch), byref(curve), byref(flag), 2)
#
# print field_strength_dbu

from propagation_model_fcurves import PropagationModelFcurvesWithoutTerrain
from propagation_model import PropagationCurve

pm = PropagationModelFcurvesWithoutTerrain()
# pl = pm.get_pathloss_coefficient_unchecked(distance=10, frequency=640, tx_height=100)

print "Pathloss at 175:", pm.get_pathloss_coefficient_unchecked(distance=10, frequency=175, tx_height=100, curve_enum=PropagationCurve.curve_50_50)
print "Pathloss at 640:", pm.get_pathloss_coefficient_unchecked(distance=10, frequency=640, tx_height=100, curve_enum=PropagationCurve.curve_50_50)
print "Pathloss at 660:", pm.get_pathloss_coefficient_unchecked(distance=10, frequency=660, tx_height=100, curve_enum=PropagationCurve.curve_50_90)

for dist in [1.5, 10, 25, 100, 200, 300]:
    for freq in [60, 175, 640]:
        for haat in [30, 100, 1000]:
            for curve in [PropagationCurve.curve_50_90, PropagationCurve.curve_50_50, PropagationCurve.curve_50_10]:
                pl = pm.get_pathloss_coefficient_unchecked(distance=dist, frequency=freq, tx_height=haat, curve_enum=curve)
                new_dist = pm.get_distance(pathloss_coefficient=pl, frequency=freq, tx_height=haat, curve_enum=curve)
                assert(abs(dist - new_dist) < .00001)

# pm.get_pathloss_coefficient_unchecked(distance=10, frequency=20, tx_height=100)


for freq in [60, 175, 640]:
    for dBu in [-10, 10, 100]:
        assert(abs(dBu - pm.dBm_to_dBu(pm.dBu_to_dBm(dBu, freq), freq)) < .000001)

for dBm in [-10, 10, 100]:
    assert(abs(dBm - pm.Watts_to_dBm(pm.dBm_to_Watts(dBm))) < .000001)




# try:
#     pm.get_pathloss_coefficient_unchecked(distance=0, frequency=100, tx_height=2000)
# except Exception as e:
#     print("Caught exception:", str(e))

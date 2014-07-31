from propagation_model_free_space import PropagationModelFreeSpace

pm = PropagationModelFreeSpace()
freq = 640
pl = pm.get_pathloss_coefficient_unchecked(10, freq)
print "Pathloss at a distance of 10 km:", pl

d = pm.get_distance(pl, freq)
print "Distance predicted from pathloss:", d

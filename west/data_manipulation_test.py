import data_manipulation
import data_manipulation_test_base
import unittest
import numpy
import data_map


class EqualDataEqualWeightsCDFTestCase(data_manipulation_test_base.AbstractCDFTestCase):
    def setUp(self):
        self.data_values = '1 1; 1 1'
        self.weight_values = '1 1; 1 1'
        self.mask_values = None

        self.expected_average = 1
        self.expected_median = 1
        self.expected_cdfx = '1 1 1 1'
        self.expected_cdfy = '.25 .5 .75 1'

        self._make_cdf()


class UnequalDataEqualWeightsCDFTestCase(data_manipulation_test_base.AbstractCDFTestCase):
    def setUp(self):
        self.data_values = '4 1; 3 2'
        self.weight_values = '1 1; 1 1'
        self.mask_values = None

        self.expected_average = 2.5
        self.expected_median = 2
        self.expected_cdfx = '1 2 3 4'
        self.expected_cdfy = '.25 .5 .75 1'

        self._make_cdf()


class MaskedDataCDFTestCase(data_manipulation_test_base.AbstractCDFTestCase):
    """
    Only the first two entries will count.
    """
    def setUp(self):
        self.data_values = '1 2; 3 4'
        self.weight_values = '1 1; 1 1'
        self.mask_values = '1 1; 0 0'

        self.expected_average = 1.5
        self.expected_median = 1
        self.expected_cdfx = '1 2'
        self.expected_cdfy = '.5 1'

        self._make_cdf()


class NonbinaryMaskCDFTestCase(data_manipulation_test_base.AbstractCDFTestCase):
    """
    Same data as :class:`MaskedDataCDFTestCase` but with non-binary mask values.
    """

    def setUp(self):
        self.data_values = '1 2; 3 4'
        self.weight_values = '1 1; 1 1'
        self.mask_values = '5 1; 0 0'

        self.expected_average = 1.5
        self.expected_median = 1
        self.expected_cdfx = '1 2'
        self.expected_cdfy = '.5 1'

        self._make_cdf()


class ZeroWeightedDataMaskCDFTestCase(data_manipulation_test_base.AbstractCDFTestCase):
    """
    Same data as :class:`MaskedDataCDFTestCase` but with non-binary mask values.
    """

    def setUp(self):
        self.data_values = '1 2; 3 4'
        self.weight_values = '0 1; 0 0'
        self.mask_values = None

        self.expected_average = 2
        self.expected_median = 2
        self.expected_cdfx = '1 2 3 4'
        self.expected_cdfy = '0 1 1 1'

        self._make_cdf()


class WeightedDataMaskCDFTestCase(data_manipulation_test_base.AbstractCDFTestCase):
    """
    Using more realistic weights.
    """

    def setUp(self):
        self.data_values = '1 2; 3 4'
        self.weight_values = '5 1; 1 1'
        self.mask_values = None

        self.expected_average = 14.0/8      # = (5*1 + 2 + 3 + 4)/(5 + 1 + 1 + 1)
        self.expected_median = 1
        self.expected_cdfx = '1 2 3 4'
        self.expected_cdfy = '0.625 0.75 0.875 1'   # 5/8 6/8 7/8 8/8

        self._make_cdf()


class LargerDataCDFTestCase(data_manipulation_test_base.AbstractCDFTestCase):

    def setUp(self):
        self.data_values = [[1, 2], [3, 4], [5, 6]]
        self.weight_values = [[1, 1], [1, 1], [1, 1]]
        self.mask_values = None

        self.expected_average = 21/6.0
        self.expected_median = 3
        self.expected_cdfx = '1 2 3 4 5 6'
        # self.expected_cdfy = ''

        self._make_cdf()


class NanDataAndWeightsMaskCDFTestCase(data_manipulation_test_base.AbstractCDFTestCase):
    """
    Using more realistic weights.
    """

    def setUp(self):
        self.data_values = [[numpy.inf, numpy.nan], [3, 4], [5, 6]]
        self.weight_values = [[1, 1], [numpy.inf, numpy.nan], [1, 1]]
        self.mask_values = None

        self.expected_average = 5.5
        self.expected_median = 5
        self.expected_cdfx = '0 0 0 0 5 6'
        self.expected_cdfy = '0 0 0 0 0.5 1'

        self._make_cdf()


class ComparableDataMapTestCase(data_manipulation_test_base.AbstractCDFTestCase):

    def setUp(self):
        test_data_map = data_map.DataMap2DBayArea.create(2, 3)
        test_data_map.reset_all_values(1)

        test_weight_map = data_map.DataMap2DBayArea.create(2, 3)
        test_weight_map.reset_all_values(1)

        self.cdfX, self.cdfY, self.average, self.median =\
            data_manipulation.calculate_cdf_from_datamap2d(test_data_map, test_weight_map)

        self.expected_average = 1
        self.expected_median = 1


class IncomparableDataMapTestCase(unittest.TestCase):
    def runTest(self):
        self.test_data_map = data_map.DataMap2DBayArea.create(2, 3)
        self.test_weight_map = data_map.DataMap2DWisconsin.create(2,3)
        self.assertRaises(TypeError, data_manipulation.calculate_cdf_from_datamap2d, self.test_data_map,
                          self.test_weight_map)


class NotDataMapTestCase(unittest.TestCase):
    def runTest(self):
        test_map = data_map.DataMap2DBayArea.create(2, 3)
        test_map.reset_all_values(1)
        # test_weight_map = data_map.DataMap2DBayArea.create(2, 3)
        # test_mask_map = data_map.DataMap2DBayArea.create(2, 3)

        bad_data_array =[1, [1, 2], numpy.matrix('1 2; 3 4'), None]

        for bad_data in bad_data_array:
            self.assertRaises(TypeError, data_manipulation.calculate_cdf_from_datamap2d, data_map=bad_data,
                              weight_map=test_map,
                              mask_map=test_map)
            if bad_data is not None:
                self.assertRaises(TypeError, data_manipulation.calculate_cdf_from_datamap2d, data_map=test_map,
                                  weight_map=bad_data,
                                  mask_map=test_map)
            if bad_data is not None:
                self.assertRaises(TypeError, data_manipulation.calculate_cdf_from_datamap2d, data_map=test_map,
                                  weight_map=test_map,
                                  mask_map=bad_data)

from custom_logging import getCurrentLogLevel, changeLogLevel, disableLogging
original_log_level = getCurrentLogLevel()
disableLogging()
unittest.main()
changeLogLevel(original_log_level)

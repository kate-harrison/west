from data_manipulation import calculate_cdf_from_matrices
# import data_map
import numpy
import unittest


class AbstractCDFTestCase(unittest.TestCase):
    def _make_cdf(self, ):
        data_matrix, weight_matrix, mask_matrix = self._create_matrices(self.data_values, self.weight_values, self.mask_values)
        (self.cdfX, self.cdfY, self.average, self.median) = calculate_cdf_from_matrices(data_matrix, weight_matrix,
                                                                                        mask_matrix)

    def _create_matrices(self, data_values, weight_values, mask_values=None):
        data_matrix = numpy.matrix(data_values)
        weight_matrix = numpy.matrix(weight_values)
        if mask_values is None:
            mask_matrix = numpy.ones(numpy.shape(data_matrix))
        else:
            mask_matrix = numpy.matrix(mask_values)
        return data_matrix, weight_matrix, mask_matrix

    def _is_monotonic_nondecreasing(self, array):
        difference = numpy.diff(array)
        return numpy.all(difference >= 0)

    def test_cdfx_monotonic_nondecreasing(self):
        self.assertTrue(self._is_monotonic_nondecreasing(self.cdfX))

    def test_cdfy_monotonic_nondecreasing(self):
        self.assertTrue(self._is_monotonic_nondecreasing(self.cdfX))

    def test_average(self):
        if hasattr(self, "expected_average"):
            self.assertAlmostEqual(self.average, self.expected_average)

    def test_median(self):
        if hasattr(self, "expected_median"):
            self.assertAlmostEqual(self.median, self.expected_median)

    def test_cdfx(self):
        if hasattr(self, "expected_cdfx"):
            expected_cdfx_array = numpy.matrix(self.expected_cdfx).A1
            self.assertTrue(numpy.allclose(self.cdfX, expected_cdfx_array))

    def test_cdfy(self):
        if hasattr(self, "expected_cdfy"):
            expected_cdfy_array = numpy.matrix(self.expected_cdfy).A1
            self.assertTrue(numpy.allclose(self.cdfY, expected_cdfy_array))



# class AbstractMapCDFTestCase(unittest.TestCase):
#
#

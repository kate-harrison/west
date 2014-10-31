import helpers
import unittest


class IndexFindingTestCase(unittest.TestCase):
    def test_find_first_value_above_or_equal(self):
        # 0 to 9.5 in increments of 0.5
        list_to_search = [l / 2.0 for l in range(0, 20)]

        # Should work without a problem
        for value in [v / 3.0 for v in range(-3, int(max(list_to_search) * 3))]:
            index = helpers.find_first_value_above_or_equal(list_to_search,
                                                            value)
            self.assertIsNotNone(index, msg="Value = %2.2f" % value)
            self.assertGreaterEqual(list_to_search[index], value,
                                    msg="Value = %2.2f" % value)
            if index > 0:
                self.assertGreaterEqual(value, list_to_search[index - 1],
                                        msg="Value = %2.2f" % value)

        # Should return None since there is no such index for this value (it
        # is greater than everything in the list)
        index = helpers.find_first_value_above_or_equal(list_to_search,
                                                        max(list_to_search) + 1)
        self.assertIsNone(index)

    def test_find_last_value_below_or_equal(self):
        # 0 to 9.5 in increments of 0.5
        list_to_search = [l / 2.0 for l in range(0, 20)]

        # Should work without a problem
        for value in [v / 3.0 for v in range(1, int(max(list_to_search) * 3))]:
            index = helpers.find_last_value_below_or_equal(list_to_search,
                                                           value)
            self.assertIsNotNone(index, msg="Value = %2.2f" % value)
            self.assertGreaterEqual(value, list_to_search[index],
                                    msg="Value = %2.2f" % value)
            if index < len(list_to_search):
                self.assertGreaterEqual(list_to_search[index + 1], value)

        # Should return None since there is no such index for this value (it
        # is less than everything in the list)
        index = helpers.find_last_value_below_or_equal(list_to_search,
                                                       min(list_to_search) - 1)
        self.assertIsNone(index)

    def test_find_first_value_approximately_equal(self):
        # 0 to 9.5 in increments of 0.5
        list_to_search = [l / 2.0 for l in range(0, 20)]

        # Should work for elements that are in the list
        for value in list_to_search:
            index = helpers.find_first_value_approximately_equal(list_to_search,
                                                                 value)
            self.assertIsNotNone(index)
            self.assertAlmostEqual(value, list_to_search[index],
                                   msg="Value = %2.2f" % value)

        # Should return None for elements that are not in the list
        for value in [-10, 200, 43]:
            index = helpers.find_first_value_approximately_equal(list_to_search,
                                                                 value)
            self.assertIsNone(index, msg="Value = %2.2f" % value)

    def test_lists_are_almost_equal(self):
        # 0 to 9.5 in increments of 0.5
        base_list = [l / 2.0 for l in range(0, 20)]

        # A list should be equal to itself
        self.assertTrue(helpers.lists_are_almost_equal(base_list, base_list))

        # Change the elements by more than the tolerance
        altered_list = [x + 0.1 for x in base_list]
        self.assertFalse(helpers.lists_are_almost_equal(base_list, altered_list,
                                                        tolerance=1e-2))

        # Change the elements by less than the tolerance
        altered_list = [x + 1e-6 for x in base_list]
        self.assertTrue(helpers.lists_are_almost_equal(base_list, altered_list,
                                                       tolerance=1e-5))


unittest.main()

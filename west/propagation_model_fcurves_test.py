import unittest
from propagation_model_fcurves import PropagationModelFcurvesWithoutTerrain
from propagation_model import PropagationCurve, InvalidDistanceError


class UnitConversionTestCase(unittest.TestCase):
    """
    Test unit conversion using known values derived from github.com/kate-harrison/whitespace-eval
    (see functions get_dBm_to_W, get_W_to_dBm, get_dBm_to_dBu, get_dBu_to_dBm).
    """

    def setUp(self):
        self.pm = PropagationModelFcurvesWithoutTerrain()

    def test_dbu_to_dbm(self):
        # 100 dBu on channel 5
        self.assertAlmostEqual(self.pm.dBu_to_dBm(100, 79), -11.799999999999997)

        # 100 dBu on channel 10
        self.assertAlmostEqual(self.pm.dBu_to_dBm(100, 195), -20.799999999999997)

        # 100 dBu on channel 23
        self.assertAlmostEqual(self.pm.dBu_to_dBm(100, 527), -29.458709988742612)

        # 100 dBu on channel 50
        self.assertAlmostEqual(self.pm.dBu_to_dBm(100, 689), -31.786882122644187)

        # 500 dBu on channel 15
        self.assertAlmostEqual(self.pm.dBu_to_dBm(500, 479), 3.713707920472170e+02)

    def test_dbm_to_dbu(self):
        # 100 dBu on channel 5
        self.assertAlmostEqual(self.pm.dBm_to_dBu(-11.799999999999997, 79), 100)

        # 100 dBu on channel 10
        self.assertAlmostEqual(self.pm.dBm_to_dBu(-20.799999999999997, 195), 100)

        # 100 dBu on channel 23
        self.assertAlmostEqual(self.pm.dBm_to_dBu(-29.458709988742612, 527), 100)

        # 100 dBu on channel 50
        self.assertAlmostEqual(self.pm.dBm_to_dBu(-31.786882122644187, 689), 100)

        # 500 dBu on channel 15
        self.assertAlmostEqual(self.pm.dBm_to_dBu(3.713707920472170e+02, 479), 500)

    def test_dbm_to_watts(self):
        self.assertAlmostEqual(self.pm.dBm_to_Watts(5),  0.003162277660168)
        self.assertAlmostEqual(self.pm.dBm_to_Watts(100), 10000000)
        self.assertAlmostEqual(self.pm.dBm_to_Watts(500), 1.000000000000000e+47)

    def test_watts_to_dbm(self):
        self.assertAlmostEqual(self.pm.Watts_to_dBm(0.003162277660168), 5)
        self.assertAlmostEqual(self.pm.Watts_to_dBm(10000000), 100)
        self.assertAlmostEqual(self.pm.Watts_to_dBm(1.000000000000000e+47), 500)


class FcurvesTestCase(unittest.TestCase):
    """
    Checking values against http://www.fcc.gov/encyclopedia/fm-and-tv-propagation-curves

    Does not seem to support target dBu > 103 or < 10
    """

    def setUp(self):
        self.pm = PropagationModelFcurvesWithoutTerrain()
        self.longMessage = True

    def test_dbu_prediction_for_us_channel_12(self):
        expected_values = list()
        expected_values.append((10.058, 89))     # (distance in km, result in dBu)
        expected_values.append((5.312, 100))
        expected_values.append((40.742, 60))
        expected_values.append((162.928, 20))
        expected_values.append((239.400, 10))
        expected_values.append((9.489, 90))

        freq_mhz = 207      # US channel 12
        input_power_watts = 400e3
        tx_haat_meters = 30
        curve = PropagationCurve.curve_50_90

        for (dist_km, target_dBu) in expected_values:
            received_dBu = self.pm.Watts_to_dBu(self.pm.get_pathloss_coefficient(frequency=freq_mhz,
                                                                                 tx_height=tx_haat_meters,
                                                                                 curve_enum=curve,
                                                                                 distance=dist_km)*input_power_watts,
                                                freq_mhz)
            # 1 decimal of precision
            self.assertAlmostEqual(received_dBu, target_dBu, 1, msg=self._target_dbu_failure_msg(target_dBu))

    def test_dbu_prediction_for_us_channel_5(self):
        expected_values = list()
        expected_values.append((3.154, 102.9))        # (distance in km, result in dBu)
        expected_values.append((3.741, 100))
        expected_values.append((45.681, 50))
        expected_values.append((208.363, 10))

        freq_mhz = 79      # US channel 5
        input_power_watts = 200e3
        tx_haat_meters = 30
        curve = PropagationCurve.curve_50_90

        for (dist_km, target_dBu) in expected_values:
            received_dBu = self.pm.Watts_to_dBu(self.pm.get_pathloss_coefficient(frequency=freq_mhz,
                                                                                 tx_height=tx_haat_meters,
                                                                                 curve_enum=curve,
                                                                                 distance=dist_km)*input_power_watts,
                                                freq_mhz)
            # 1 decimal of precision
            self.assertAlmostEqual(received_dBu, target_dBu, 1, msg=self._target_dbu_failure_msg(target_dBu))

    def test_dbu_prediction_for_us_channel_25(self):
        expected_values = list()
        expected_values.append((9.605, 100))        # (distance in km, result in dBu)
        expected_values.append((66.657, 50))
        expected_values.append((125.821, 20))
        expected_values.append((172.619, 10))
        expected_values.append((7.952, 103))

        freq_mhz = 539      # US channel 25
        input_power_watts = 100e3
        tx_haat_meters = 300
        curve = PropagationCurve.curve_50_90

        for (dist_km, target_dBu) in expected_values:
            received_dBu = self.pm.Watts_to_dBu(self.pm.get_pathloss_coefficient(frequency=freq_mhz,
                                                                                 tx_height=tx_haat_meters,
                                                                                 curve_enum=curve,
                                                                                 distance=dist_km)*input_power_watts,
                                                freq_mhz)
            # 1 decimal of precision
            self.assertAlmostEqual(received_dBu, target_dBu, 1, msg=self._target_dbu_failure_msg(target_dBu))

    def test_dbu_prediction_for_f_50_10(self):
        expected_values = list()
        expected_values.append((10.058, 89))     # (distance in km, result in dBu)
        expected_values.append((5.312, 100))
        expected_values.append((64.202, 60))
        expected_values.append((284.765, 20))
        expected_values.append((9.489, 90))

        freq_mhz = 207      # US channel 12
        input_power_watts = 400e3
        tx_haat_meters = 30
        curve = PropagationCurve.curve_50_10

        for (dist_km, target_dBu) in expected_values:
            received_dBu = self.pm.Watts_to_dBu(self.pm.get_pathloss_coefficient(frequency=freq_mhz,
                                                                                 tx_height=tx_haat_meters,
                                                                                 curve_enum=curve,
                                                                                 distance=dist_km)*input_power_watts,
                                                freq_mhz)
            # 1 decimal of precision
            self.assertAlmostEqual(received_dBu, target_dBu, 1, msg=self._target_dbu_failure_msg(target_dBu))

    def _target_dbu_failure_msg(self, target_dBu):
        return "\n\nFailed for target dBu = %2.2f" % target_dBu


    def test_out_of_bounds_errors_are_raised(self):
        curve = PropagationCurve.curve_50_10

        # Distance > 300
        for distance in [301, 400, 500]:
            with self.assertRaises(InvalidDistanceError,
                                   msg="\n\nFailed for distance = %2.2f km" %
                                   distance):
                self.pm.get_pathloss_coefficient(frequency=207, tx_height=30, curve_enum=curve, distance=distance)

        # Unsupported frequencies
        for frequency in [53, 89, 173, 217, 469, 891]:
            with self.assertRaises(ValueError, msg="\n\nFailed for frequency = %d MHz" % frequency):
                self.pm.get_pathloss_coefficient(frequency=frequency, tx_height=30, curve_enum=curve, distance=10)

    def test_missing_input_errors_are_raised(self):
        curve = PropagationCurve.curve_50_10

        # get_pathloss_coefficient
        with self.assertRaises(AttributeError, msg="Missing frequency"):
            self.pm.get_pathloss_coefficient(tx_height=30, curve_enum=curve, distance=10)
        with self.assertRaises(AttributeError, msg="Missing transmitter height"):
            self.pm.get_pathloss_coefficient(distance=10, frequency=207, curve_enum=curve)
        with self.assertRaises(AttributeError, msg="Missing curve specification"):
            self.pm.get_pathloss_coefficient(frequency=207, tx_height=30, distance=10)
        with self.assertRaises(TypeError, msg="Missing distance"):
            self.pm.get_pathloss_coefficient(frequency=207, tx_height=30, curve_enum=curve)

        # get_distance
        pathloss = 1e-9
        with self.assertRaises(AttributeError, msg="Missing frequency"):
            self.pm.get_distance(tx_height=30, curve_enum=curve, pathloss_coefficient=pathloss)
        with self.assertRaises(AttributeError, msg="Missing transmitter height"):
            self.pm.get_distance(pathloss_coefficient=pathloss, frequency=207, curve_enum=curve)
        with self.assertRaises(AttributeError, msg="Missing curve specification"):
            self.pm.get_distance(frequency=207, tx_height=30, pathloss_coefficient=pathloss)
        with self.assertRaises(TypeError, msg="Missing pathloss coefficient"):
            self.pm.get_distance(frequency=207, tx_height=30, curve_enum=curve)

    def test_function_inverses(self):
        for dist in [1.5, 10, 25, 100, 200, 300]:
            for freq in [60, 175, 640]:
                for haat in [30, 100, 1000]:
                    for curve in [PropagationCurve.curve_50_90, PropagationCurve.curve_50_50, PropagationCurve.curve_50_10]:
                        pl = self.pm.get_pathloss_coefficient_unchecked(distance=dist, frequency=freq, tx_height=haat, curve_enum=curve)
                        new_dist = self.pm.get_distance(pathloss_coefficient=pl, frequency=freq, tx_height=haat, curve_enum=curve)
                        self.assertAlmostEqual(dist, new_dist)

    def test_conversion_inverses(self):
        for freq in [60, 175, 640]:
            for dBu in [-10, 10, 100]:
                self.assertAlmostEqual(dBu, self.pm.dBm_to_dBu(self.pm.dBu_to_dBm(dBu, freq), freq))

        for dBm in [-10, 10, 100]:
            self.assertAlmostEqual(dBm, self.pm.Watts_to_dBm(self.pm.dBm_to_Watts(dBm)))

unittest.main()

"""Unit tests for the DC bias engineering module."""

import unittest

from dc_bias import BiasError, solve


class TestReferenceOperatingPoint(unittest.TestCase):
    def test_reference_operating_point(self):
        r = solve(
            vcc=12,
            r1=100_000,
            r2=22_000,
            rc=2_200,
            re=1_000,
            beta=100,
            vbe=0.70,
        )

        self.assertAlmostEqual(r["vth"], 2.163934, places=4)
        self.assertAlmostEqual(r["rth"], 18032.787, places=2)
        self.assertAlmostEqual(r["ib"], 1.229868e-5, places=7)
        self.assertAlmostEqual(r["ic"], 1.229868e-3, places=6)
        self.assertAlmostEqual(r["ie"], 1.242167e-3, places=6)
        self.assertAlmostEqual(r["ve"], 1.242167, places=4)
        self.assertAlmostEqual(r["vb"], 1.942167, places=4)
        self.assertAlmostEqual(r["vc"], 9.294290, places=4)
        self.assertAlmostEqual(r["vce"], 8.052123, places=4)


class TestValidation(unittest.TestCase):
    def _base(self, **overrides):
        params = dict(
            vcc=12, r1=100_000, r2=22_000, rc=2_200, re=1_000, beta=100, vbe=0.70
        )
        params.update(overrides)
        return params

    def test_zero_and_negative_resistance_rejected(self):
        for bad in (dict(r1=0), dict(r2=0), dict(rc=-1), dict(re=0)):
            with self.assertRaises(BiasError):
                solve(**self._base(**bad))

    def test_invalid_vcc_and_beta_rejected(self):
        for bad in (dict(vcc=0), dict(beta=0), dict(beta=-5), dict(vcc=-12)):
            with self.assertRaises(BiasError):
                solve(**self._base(**bad))

    def test_vbe_must_be_below_vcc(self):
        for bad in (dict(vbe=0), dict(vbe=12), dict(vbe=13)):
            with self.assertRaises(BiasError):
                solve(**self._base(**bad))


class TestOperatingRegion(unittest.TestCase):
    def _base(self, **overrides):
        params = dict(
            vcc=12, r1=100_000, r2=22_000, rc=2_200, re=1_000, beta=100, vbe=0.70
        )
        params.update(overrides)
        return solve(**params)

    def test_region_active_no_warning(self):
        r = self._base()
        self.assertEqual(r["region"], "active")
        self.assertEqual(r["warnings"], [])

    def test_cutoff_when_vth_below_vbe(self):
        r = self._base(r2=1_000)
        self.assertEqual(r["region"], "cutoff")
        self.assertEqual(r["ic"], 0.0)
        self.assertEqual(r["ie"], 0.0)
        self.assertAlmostEqual(r["vce"], 12.0, places=6)
        self.assertTrue(r["warnings"])

    def test_saturation_warning(self):
        r = self._base(rc=47_000)
        self.assertEqual(r["region"], "saturation")
        self.assertLess(r["vce"], 0.2)
        self.assertTrue(any("Saturation" in w for w in r["warnings"]))


class TestModuleInputCoercion(unittest.TestCase):
    def test_non_numeric_string_rejected(self):
        with self.assertRaises(BiasError):
            solve("abc", 100_000, 22_000, 2_200, 1_000, 100, 0.70)

    def test_nan_and_infinity_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(BiasError):
                solve(bad, 100_000, 22_000, 2_200, 1_000, 100, 0.70)


if __name__ == "__main__":
    unittest.main()

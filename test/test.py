from src.calculations import ZscoreWeight, ZscoreHeight, interpolate_lms
from src.database import Child, get_growth_table
import pandas as pd
from pathlib import Path
import unittest

class TestZscoreWeight(unittest.TestCase):
    def test_zscore1(self):
        bmi = 30
        z = ZscoreWeight(-1.7862, 16.9392, 0.11070, bmi)
        self.assertEqual(z.zscore(), 3.35)

    def test_zscore2(self):
        bmi = 14
        z = ZscoreWeight(-1.3529, 20.4951, 0.12579, bmi)
        self.assertEqual(z.zscore(), -3.80)

    def test_zscore3(self):
        bmi = 19
        z = ZscoreWeight(-1.6318, 16.0490, 0.10038, bmi)
        self.assertEqual(z.zscore(), 1.47)


if __name__=='__main__':
	unittest.main()
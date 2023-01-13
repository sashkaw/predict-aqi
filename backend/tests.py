import numpy as np
import pandas as pd
from pandas import testing as tm
from django.test import TestCase
from .views import *

# Create your tests here.
class Difference(TestCase):
    def setUp(self):
        self.data = [1,2,3,5]
        self.expected = pd.Series([None, None, 2.0, 3.0])
        self.interval = 2
    #@skip("Writing tests...")
    def test_diff(self):
        result = difference(dataset=self.data, interval=self.interval)
        tm.assert_series_equal(result, self.expected)

class CalcNowCast(TestCase):
    def setUp(self):
        self.data = [1,2,3,6]
        self.expected = 13/3

    def test_nowcast(self):
        result = now_cast_pm(self.data)
        self.assertEqual(result, self.expected)


# Imports
from random import randint, seed
from decimal import Decimal
import numpy as np
from numpy import testing as npt
import pandas as pd
from pandas import testing as pdt
from django.test import TestCase
from .views import *
from .apps import BackendConfig

# Create your tests here.
class Difference(TestCase):
    def setUp(self):
        self.data = [1, 2, 3, 5]
        self.expected = pd.Series([None, None, 2.0, 3.0])
        self.interval = 2

    # @skip("Writing tests...")
    def test_diff(self):
        result = difference(dataset=self.data, interval=self.interval)
        pdt.assert_series_equal(result, self.expected)


class CalcNowCast(TestCase):
    def setUp(self):
        self.data = [1, 2, 3, 6]
        self.expected = 13/3

    def test_nowcast(self):
        result = nowcast_pm(self.data)
        self.assertEqual(result, self.expected)


class DiffScale(TestCase):
    def setUp(self):
        self.data = [1, 2, 3, 5]
        # Scaler for transforming data between [-1, 1]
        self.scaler = BackendConfig.scaler
        self.expected = np.array(
            [[0.04217757],
             [0.04217757],
             [0.05393659]])

    def test_diff_scale(self):
        result = diff_scale(
            data=self.data,
            scaler=self.scaler,
            interval=1,
            return_arr=False)
        # Compare numpy arrays with specified decimal precision
        npt.assert_array_almost_equal(x=self.expected, y=result, decimal=6)


class InvertScaleDiff(TestCase):
    def setUp(self):
        self.forecast = np.array(
            [[0.04217757],
             [0.04217757],
             [0.05393659]])
        self.previous_ts = np.array([
            [[1, 2, 3, 5]]
        ])
        # Scaler for transforming data between [-1, 1]
        self.scaler = BackendConfig.scaler
        self.ts_in = 4
        self.ts_out = 4
        self.expected = np.array(
            [[1.99999965],
             [1.99999965],
             [3.00000005]])

    def test_invert_scale_diff(self):
        result = invert_scale_diff(
            yhat=self.forecast,
            prev=self.previous_ts,
            scaler=self.scaler,
            steps_in=self.ts_in,
            steps_out=self.ts_out)
        # Compare numpy arrays with specified decimal precision
        npt.assert_array_almost_equal(x=self.expected, y=result, decimal=6)


class ForecastAQI(TestCase):
    def setUp(self):
        # Create random test data
        self.ts_in = 24
        self.ts_out = 12
        # Set random seed
        seed(10)
        # Create list to hold the random data
        self.data = list()
        # Populate list with random integers between 0 and 200
        for i in range(self.ts_in + 1):
            rand_n = randint(0, 200)
            self.data.append(rand_n)
        # Load scaler
        self.scaler = BackendConfig.scaler
        # Get scaled versions of X_raw
        self.X_scaled = diff_scale(
            self.data,  # Scale raw data
            scaler=self.scaler,
            return_arr=True)
        # Get X_raw for inverting differencing
        # Note: use [1:] because we want the most recent values
        self.X_raw = self.data[1:]
        self.expected = [Decimal('191'),
                         Decimal('187'),
                         Decimal('165'),
                         Decimal('65'),
                         Decimal('155'),
                         Decimal('240'),
                         Decimal('170'),
                         Decimal('46'),
                         Decimal('178'),
                         Decimal('99'),
                         Decimal('204'),
                         Decimal('169')]

    def test_forecast_aqi(self):
        # Generate forecast from test data
        result = forecast_aqi(
            X_scaled=self.X_scaled,
            X_raw=self.X_raw,
            scaler=self.scaler)
        # Compare numpy arrays with specified decimal precision
        npt.assert_array_almost_equal(x=self.expected, y=result, decimal=6)

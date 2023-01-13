# IMPORTS
import numpy as np
import pandas as pd
import requests
from time import mktime
from datetime import datetime, timedelta
import aqi as AQIConverter
from .apps import *
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# CONSTANTS
# URL for external API call
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/air_pollution/history'
# Batch size for model prediction
BATCH_SIZE = 32
# Number of hours for NowCast window average
NOWCAST_WINDOW = 12
# Time steps for model
STEPS_IN = 24
STEPS_OUT = 12

# VIEWS
class Prediction(APIView):
    '''
    Get current air quality data from external api and forecast future air quality.
    '''
    def fetch_current_data(self):
        '''
        Make request to external API to get current air quality data.

        Return:
        1) time_series --- list of numeric air quality time series data
        2) -1 on failure
        '''
        # Create url from params

        # Specify position for API query
        lat = 44.026280
        long = -123.083715

        # Get the most recent hour, on the dot
        d2 = datetime.now().replace(microsecond=0, second=0, minute=0)
        one_hr = timedelta(hours=1)
        # Get one hour before the most recent hour
        d1 = d2 - one_hr
        # Convert to unix time for API call
        d1_unix = int(mktime(d1.timetuple()))
        d2_unix = int(mktime(d2.timetuple()))

        # Specify query parameters for API call
        params = {
            'lat': lat,
            'lon': long,
            'start': d1_unix,
            'end': d2_unix,
            'appid': settings.WEATHER_API_KEY,
        }

        # Fetch data from external API
        try:
            api_response = requests.get(url=WEATHER_API_URL, params=params)
            api_json = api_response.json()
            # Extract air quality data
            api_data = list(api_json.get('list', {}))
            time_series = list()
            # Extract air quality data of interest
            for item in api_data:
                current_val = item.get('components', {}).get('pm2_5', None)
                time_series.append(current_val)

            #print(time_series)
            return time_series
        except:
            return -1
        
    def get(self, request):
        '''
        Call fetch request to get current air quality data. 
        Make prediction for future air quality based on current air quality.

        Return:
        1) Successful Response object with air quality prediction, OR
        2) Error response if external API failed
        '''

        # Get current air quality data
        current_pm2_5 = self.fetch_current_data()

        # If we got valid data
        if(current_pm2_5 != -1):
            # Convert current PM2.5 value to Intermediate AQI using the US EPA method
            # (Intermediate means calculated from a single pollutant)
            aqi_current = AQIConverter.to_iaqi(AQIConverter.POLLUTANT_PM25, str(current_pm2_5[1]), algo=AQIConverter.ALGO_EPA)
            #print(aqi_current)

            # Generate Intermediate AQI forecast based on current
            aqi_forecast = forecast_aqi(current_pm2_5)

            context = {
                'current_aqi': aqi_current,
                'forecast_aqi': aqi_forecast,
                }

            return Response(context, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        

# HELPER FUNCTIONS
# Transform time series to stationary:
# Create a differenced series to remove any increasing trend
def difference(dataset, interval=1):
    diff = [None] * interval # Start with null value(s) so length matches the other data frames
    # Iterate through 1 - n records
    for i in range(interval, len(dataset)):
        # Calculate difference between current and timestep and past timestep
        value = dataset[i] - dataset[i - interval]
        diff.append(value)

    return pd.Series(diff)

# Need to calculate 12 hr weighted averages for EPA NowCast methodology
# See: https://usepa.servicenowservices.com/airnow?id=kb_article_view&sys_id=bb8b65ef1b06bc10028420eae54bcb98&spa=1
# Use rolling `apply` for every 12 hrs
# This will generate a new col of NowCast values that takes into context the previous 12 hrs
# Then for the forecast we could train the model to forecast the next 24 - 48 hrs


def now_cast_pm(input_arr):
    '''
    Apply EPA NowCast algorithm on sequence of timeseries (excluding final stage of converting to AQI).

    Parameters:
    input_arr --- nd array or list containing air quality particulate matter time series

    Returns:
    now_cast -- numeric weighted average of timeseries values in same units as original time series data
    '''
    # Select the minimum and maximum PM measurements.
    min_val, max_val = min(input_arr), max(input_arr)
    # Subtract the minimum measurement from the maximum measurement to get the range.
    arr_range = max_val - min_val
    # Divide the range by the maximum measurement in the 12 hour period to get the scaled rate of change.
    rate_of_change = arr_range / max_val
    # Subtract the scaled rate of change from 1 to get the weight factor. 
    # The weight factor must be between .5 and 1. The minimum limit approximates a 3-hour average.
    weight_factor = 1 - rate_of_change
    #If the weight factor is less than 0.5, then set it equal to 0.5.
    if(weight_factor < 0.5):
        weight_factor = 0.5

    # Multiply each hourly measurement by the weight factor raised to the 
    # power of the number of hours ago the value was measured 
    # (for the current hour, the factor is raised to the zero power).
    weight_factor_pow = list()
    products = list()
    for i, val in enumerate(list(reversed(input_arr))):
        wf_pow = pow(weight_factor, i)
        weight_factor_pow.append(wf_pow)
        products.append(val * wf_pow)
        
    # Compute the NowCast by summing the products from Step 6 and 
    # dividing by the sum of the weight factor raised to the power
    # of the number of hours ago each value was measured.
    now_cast = (sum(products)) / (sum(weight_factor_pow))
    return now_cast

    # TODO: Eventually convert this value to an AQI. A concentration to AQI converter is available at https://airnow.gov/aqi/aqi-calculator-concentration
    

# Difference and scale data to [-1, 1]
def diff_scale(data, scaler, interval=1, return_arr=False):
    # Difference the data to remove any long term trend
    data_diff = difference(data, interval=interval)
    # Slice array to ignore first 'interval' # of elements (null) and convert to 2-D numpy array for scaler
    data_diff = np.array(data_diff[interval:])
    # Reshape into array for scaler (observations, features)
    data_diff = data_diff.reshape(len(data_diff), 1)
    # Scale the data
    diff_scaled = scaler.transform(data_diff)

    # If return_arr flag is True, convert back to 1-D numpy array
    if(return_arr):
        diff_scaled = diff_scaled[:, 0]

    # Otherwise return 2-D numpy array
    return diff_scaled, scaler
 
def invert_scale_diff(yhat, prev, scaler, steps_in, steps_out):
    '''
    Invert scaling and remove differencing for forecasted values
    
    Parameters:
    yhat --- scaled and differenced forecast data as 2-D ndarray of shape [samples, timesteps]
    prev --- raw data as 3-D ndarray of shape [samples, timesteps, features]
    scaler --- trained sklearn scaler object
    steps_in --- number of input steps (Note: currently, # steps_in must be >= # steps_out)
    steps_out -- number of output steps

    Returns:
    1) inverted_rm_diff --- forecast data with no scaling/differencing as 2-D ndarray of shape [samples, timesteps], OR
    2) -1 for invalid parameters
    '''
    if(steps_in < steps_out):
        return -1

    # Wrap forecasted values in numpy array and reshape for scaler
    #array = np.array(yhat)
    #array = array.reshape(len(array))
    # Invert scaling 
    inverted = scaler.inverse_transform(yhat)
    #inverted_val = inverted[0, 0]
    # Add the previous values to the forecasted values to remove differencing

    # Take difference of steps_in and steps_out so that if we can add the two datasets without changing shape
    inverted_rm_diff = inverted + prev[:,(steps_in - steps_out):,0] # 0 is because only one feature currently

    return inverted_rm_diff

def forecast_aqi(X, X_raw):
    '''
    Transform input air quality time series data and forecast future air quality.

    Parameters:
    X --- list of numeric air quality time series data (eg [1.2, 5.0])

    Return:
    forecast_aqi --- forecasted air quality in numeric format
    '''

    # Get data scaler that was loaded on app start
    # This scaler will transform the data between -1 and 1
    scaler = BackendConfig.scaler

    # Difference and scale the data
    X_scaled = diff_scale(data=X, scaler=scaler, return_arr=True)
    
    # Get LSTM model that was loaded on app start
    model = BackendConfig.model

    # Generate forecast
    yhat_diff_scaled = model.predict(X_scaled, batch_size=BATCH_SIZE)

    # Invert scaling and differencing
    yhat = invert_scale_diff(
        yhat=yhat_diff_scaled, 
        prev=X_raw, #TODO generate X raw
        scaler=scaler, 
        steps_in=STEPS_IN, 
        steps_out=STEPS_OUT)

    # Invert data transforms on forecast
    forecast_pm2_5 = invert_scale_diff(yhat=yhat, prev=X[1], scaler=scaler)

    # Convert PM2.5 forecast to Intermediate AQI using the US EPA method
    # (Intermediate means calculated from a single pollutant)
    aqi_forecast = AQIConverter.to_iaqi(AQIConverter.POLLUTANT_PM25, str(forecast_pm2_5), algo=AQIConverter.ALGO_EPA)

    return aqi_forecast
    

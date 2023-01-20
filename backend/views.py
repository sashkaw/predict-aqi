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
# Number of time steps for differencing
DIFFERENCE_INTERVAL = 1

# VIEWS
class Prediction(APIView):
    '''
    Get current air quality data from external api and forecast future air quality.
    '''
    def fetch_current_data(self):
        '''
        Make request to external API to get current air quality data.

        Return:
        1) time_series, time_steps --- lists of numeric air quality time series data and 
            corresponding timesteps in unix time (UTC time zone)
        2) -1 on failure
        '''
        # Create url from params

        # Specify position for API query
        lat = 44.026280
        long = -123.083715

        # Get the most recent hour, on the dot
        d2 = datetime.now().replace(microsecond=0, second=0, minute=0)
        # Need to get extra data in advance so when we apply NowCast calc we don't end up with nulls
        prev_ts = timedelta(hours=STEPS_IN + NOWCAST_WINDOW - 1)
        # Get time steps before the previous hour
        d1 = d2 - prev_ts
        # Convert to unix time for API call
        d1_unix = int(mktime(d1.timetuple()))
        d2_unix = int(mktime(d2.timetuple()))

        # Calculate forward time steps for displaying forecast data
        # Note: Keep these time stamps in UTC so we can 
        # convert to local time on the frontend
        future_timesteps = list()
        for i in range(NOWCAST_WINDOW):
            # Add timesteps to most recent hour to get future time steps
            next_timestep = d2 + timedelta(hours=(i + 1))
            future_timesteps.append(next_timestep)

        formatted_API_key = settings.WEATHER_API_KEY.replace('\"', '' )
        print("formatted key:", formatted_API_key)

        # Specify query parameters for API call
        params = {
            'lat': lat,
            'lon': long,
            'start': d1_unix,
            'end': d2_unix,
            # Parse API Key to remove double quotes
            'appid': formatted_API_key,
        }

        print("params:", params)

        # Fetch data from external API
        try:
            api_response = requests.get(url=WEATHER_API_URL, params=params)
            print("api_response", api_response)
            api_json = api_response.json()
            # Extract air quality data
            api_data = list(api_json.get('list', {}))
            time_series = list()
            #time_steps = list()
            # Extract air quality data of interest
            # and corresponding time step (date) for each set of observations
            for item in api_data:
                current_val = item.get('components', {}).get('pm2_5', None)
                #current_dt = item.get('dt')
                time_series.append(current_val)
                #time_steps.append(current_dt)

            print("timeseries",  time_series)
            return time_series, future_timesteps
        except:
            print("external API error")
            return -1
        
    def get(self, request):
        '''
        Call fetch request to get current air quality data. 
        Make prediction for future air quality based on current air quality.

        Return:
        1) Successful Response object with air quality prediction, OR
        2) Error response if external API failed
        '''

        # Get current air quality data and future timesteps
        # NOTE: could add in current air quality data if desired 
        # (eg have 1 extra data point for the UI)
        current_pm2_5, future_ts = self.fetch_current_data()

        # If we got valid data
        if(current_pm2_5 != -1):
            # Convert PM value to AQI
            aqi_current = list()
            for i in current_pm2_5:
                aqi_current.append(AQIConverter.to_iaqi(AQIConverter.POLLUTANT_PM25, str(i), algo=AQIConverter.ALGO_EPA))

            # Scaler for transforming data between [-1, 1]
            scaler = BackendConfig.scaler

            # Apply NowCast function to pm2.5 data
            # Need raw=True to pass input as ndarray
            current_nowcast = pd.Series(current_pm2_5).rolling(window=NOWCAST_WINDOW).apply(nowcast_pm, raw=True)
            # Remove nulls from first window of NowCast data
            nowcast_clean = pd.Series(current_nowcast[NOWCAST_WINDOW-1:])
            nowcast_clean.reset_index(drop=True, inplace=True)

            # Difference and scale the NowCast data
            nowcast_diff = diff_scale(data=nowcast_clean, scaler=scaler, interval=DIFFERENCE_INTERVAL, return_arr=True)

            # Generate Intermediate AQI forecast based on current
            # Get only the most recent pm2.5 data because we need to add those 
            # most recent values to the forecast to get the non-differenced forecast
            aqi_forecast = forecast_aqi(X_scaled=nowcast_diff, X_raw=current_pm2_5[NOWCAST_WINDOW:], scaler=scaler)

            context = {
                'pm2.5_current': current_pm2_5,
                'aqi_current': aqi_current,
                'aqi_forecast': aqi_forecast,
                'future_timesteps': future_ts,
                }

            return Response(context, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        

# HELPER FUNCTIONS
def nowcast_pm(input_arr):
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
    
def difference(dataset, interval=1):
    ''' 
    Transform time series to stationary by differencing data to remove long term trend.

    Parameters:
    dataset --- list or ndarray of time series data
    interval (default=1) --- number of time steps for differencing

    Returns:
    pandas Series containing differenced data
    '''
    diff = [None] * interval # Start with null value(s) so length matches the other data frames
    # Iterate through 1 - n records
    for i in range(interval, len(dataset)):
        # Calculate difference between current and timestep and past timestep
        value = dataset[i] - dataset[i - interval]
        diff.append(value)

    return pd.Series(diff)

def diff_scale(data, scaler, interval=1, return_arr=False):
    '''
    Difference and scale data to [-1, 1]

    Parameters:
    data --- list or ndarray of time series data
    scaler --- scaler object for normalizing data
    interval --- number of timesteps to use for differencing
    return_arr, default=False --- boolean to specify output type (1-D numpy array if true, 2-D numpy array if False)

    Returns:
    diff_scaled --- 1-D OR 2-D numpy array (depending on return_arr flag) containing differenced timeseries values
    '''
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
    return diff_scaled

 
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

def forecast_aqi(X_scaled, X_raw, scaler):
    '''
    Transform input air quality time series data and forecast future air quality.

    Parameters:
    X_scaled --- list of scaled and differenced air quality time series data (eg [0.1, 0.3])
    X_raw --- list of corresponding raw values for the same time series (eg [2, 5])
    scaler --- scaler object for inverting the data transforms on the timeseries

    Returns:
    forecast_aqi --- forecasted air quality in numeric format
    '''
    
    # Reshape the scaled data and raw data from [timesteps] to [samples, timesteps, features]
    X_scaled_reshaped = np.array(X_scaled).reshape(1, len(X_scaled), 1)
    X_raw_reshaped = np.array(X_raw).reshape(1, len(X_raw), 1)

    # Get LSTM model that was loaded on app start
    model = BackendConfig.model

    # Generate forecast
    yhat_diff_scaled = model.predict(X_scaled_reshaped, batch_size=BATCH_SIZE)

    # Invert scaling and differencing
    yhat = invert_scale_diff(
        yhat=yhat_diff_scaled, 
        prev=X_raw_reshaped,
        scaler=scaler, 
        steps_in=STEPS_IN, 
        steps_out=STEPS_OUT)

    # Convert PM2.5 forecast to Intermediate AQI using the US EPA method
    # (Intermediate means calculated from a single pollutant)
    aqi_forecast = list()
    for i in yhat[0,:]: # Select [features, timesteps]
        aqi_forecast.append(AQIConverter.to_iaqi(AQIConverter.POLLUTANT_PM25, str(round(i, 2)), algo=AQIConverter.ALGO_EPA))

    return aqi_forecast    

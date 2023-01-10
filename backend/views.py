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

# Difference and scale data to [-1, 1]
def diff_scale(data, scaler):
    # Difference the data to remove any long term trend
    data_diff = difference(data)
    # Slice array to ignore first element (null) and convert to 2-D numpy array for scaler
    data_diff = np.array([data_diff[1:]])
    # Reshape into array for scaler (observatons, features)
    data_diff = data_diff.reshape(data_diff.shape[0], data_diff.shape[1])
    # Scale the data
    diff_scaled = scaler.transform(data_diff)

    return diff_scaled
 
# Invert scaling and remove differencing for a forecasted value
def invert_scale_diff(yhat, prev, scaler):
    # Wrap forecasted value in numpy array and reshape for scaler
    array = np.array(yhat)
    array = array.reshape(1, len(array))
    # Invert scaling 
    inverted = scaler.inverse_transform(array)
    inverted_val = inverted[0, 0]
    # Add the previous value to the forecasted value to remove differencing
    inverted_rm_diff = inverted_val + prev

    return inverted_rm_diff

def forecast_aqi(X):
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
    X_scaled = diff_scale(data=X, scaler=scaler)
    
    # Get LSTM model that was loaded on app start
    model = BackendConfig.model
    
    # Generate forecast
    yhat = model.predict(X_scaled, batch_size=BATCH_SIZE)
    #print("yhat: ", yhat)

    # Invert data transforms on forecast
    forecast_pm2_5 = invert_scale_diff(yhat=yhat, prev=X[1], scaler=scaler)

    # Convert PM2.5 forecast to Intermediate AQI using the US EPA method
    # (Intermediate means calculated from a single pollutant)
    aqi_forecast = AQIConverter.to_iaqi(AQIConverter.POLLUTANT_PM25, str(forecast_pm2_5), algo=AQIConverter.ALGO_EPA)

    return aqi_forecast
    

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
        
        






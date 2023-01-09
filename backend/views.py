import numpy as np
import pandas as pd
import requests
from time import mktime
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from .apps import *
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# Constants

WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/air_pollution/history'
#WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/air_pollution'

# Helper functions

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

# Scale data to [-1, 1]
def scale(data, scaler):
    # transform data (possibly not needed for 1d timeseries)
    data = data.reshape(data.shape[0], data.shape[1])
    data_scaled = scaler.transform(data)

    return data_scaled
 
# inverse scaling for a forecasted value
def invert_scale(scaler, yhat):
    array = np.array(yhat)
    array = array.reshape(1, len(array))
    inverted = scaler.inverse_transform(array)
    return inverted[0, 0]

def forecast_aqi(X):
    '''
    Transform input air quality time series data and forecast future air quality.

    Parameters:
    X --- list of numeric air quality time series data

    Return:
    forecast --- forecasted air quality in numeric format
    '''

    # Difference data to remove trends
    X_diff = difference(X)

    # Define batch size for model prediction
    batch_size = 4

    # Get data scaler that was loaded on app start
    # This scaler will transform the data between -1 and 1
    #scaler = BackendConfig.scaler

    # Scale the differenced data
    #aqi_scaled = scale(X_diff[1])
    
    # Get LSTM model that was loaded on app start
    #model = BackendConfig.model
    # Fit and evaluate model
    #X_trimmed = aqi_scaled[1]

    # Reshape
    #reshaped = X_trimmed.reshape(len(X_trimmed), 1, 1)
    
    # Forecast dataset
    #output = model.predict(reshaped, batch_size=batch_size)

    # Invert data transforms on forecast
    #yhat = output[0]

    # Invert scaling
    #yhat = invert_scale(scaler, X[1], yhat)

    # invert differencing
    #yhat = yhat + X[1]

    # store forecast
    #forecast = yhat

    #return forecast
    return X_diff[1]
    

# Create your views here.
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
        current_aqi = self.fetch_current_data()

        if(current_aqi != -1):
        
            #print(current_aqi)
            forecast = forecast_aqi(current_aqi)

            # Difference data to remove trend, 
            # scale between [-1, 1],
            # make prediction for next air quality value
            # using the LSTM model,
            # invert the scaling and differencing of the output
            # to match the input data format
            #forecast_aqi = forecast_aqi(current_aqi)
            
            # Make prediction based on current air quality
            #prediction = lstm_model.predict(np.array([[current_aqi]]))
            context = {
                'data': forecast,
                }

            return Response(context, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        






import numpy as np
import pandas as pd
import requests
from datetime import datetime
from .apps import *
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# Constants
#WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/air_pollution/history'
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/air_pollution'

# Create your views here.
class Prediction(APIView):
    '''
    Get current air quality data from external api and forecast future air quality.
    '''
    def fetch_current_data(self):
        '''
        Make request to external API to get current air quality data.

        Return:
        1) JSON formatted response from external API on success, OR
        2) -1 on failure
        '''
        # Create url from params

        # Specify position
        lat = 44.026280
        long = -123.083715

        # Get current time
        #date2 = datetime.utcnow()
        #date1 = datetime.utcnow() - 1000

        params = {
            'lat': lat,
            'lon': long,
            #'start': date1,
            #'end': date2,
            'appid': settings.WEATHER_API_KEY,
        }

        # Fetch data from external API
        try:
            api_response = requests.get(url=WEATHER_API_URL, params=params)
            return api_response.json()
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
        
            print(current_aqi)

            # TODO:
            # Transform data: 
            # 1) Difference from previous value
            # 2) Normalize
            
            # Get LSTM model that was loaded on app start
            #lstm_model = BackendConfig.model

            # TODO:
            # Transform data for output:
            # 1) Reverse normalization
            # 2) Add to previous value to reverse differencing
            
            # Make prediction based on current air quality
            #prediction = lstm_model.predict(np.array([[current_aqi]]))
            context = {
                'data': current_aqi, # For testing
                }

            return Response(context, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        






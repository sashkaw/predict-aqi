# predict-aqi
Django application to forecast Air Quality Index (AQI) using a Long Short-Term Memory (LSTM) neural network

## Overview
- Cleans historic air quality data and fill gaps in the time series using `numpy` and `pandas`
- Transforms the historic air quality time series to stationary to remove long term trend
- Creates a LSTM model for air quality forecasting using `TensorFlow` and `scikit-learn`
- Iteratively examines effect of model hyperparameters including learning rate and regularization
  - Note: The most recent training for the model yielded a RMSE of `~0.09` for the training data, and a RMSE of `~0.10` for the test data
- Utilizes `Django REST Framework` to create a REST API:
  - Django backend fetches current air quality data from an external API for use in forecasting air quality

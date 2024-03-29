# predict-aqi
Django + React application to forecast Air Quality Index (AQI) using a Long Short-Term Memory (LSTM) neural network

## Overview
- Cleans historic air quality data and fill gaps in the time series using `numpy` and `pandas`
- Transforms the historic air quality time series to stationary to remove long term trend
- Creates a LSTM model for air quality forecasting using `TensorFlow` and `scikit-learn`
- Iteratively examines effect of model hyperparameters including learning rate and regularization
  - Note: The most recent training for the model yielded a RMSE of `~0.09` for the training data, and a RMSE of `~0.10` for the test data
- Utilizes `Django REST Framework` to create a REST API:
  - Django backend fetches current air quality data from an external API for use in forecasting air quality
 - Uses `React.js` to fetch data from backend API and create frontend forecast interface

<br>

 ![User interface snapshot](images/ui.png)
 
 <br>

## How to use this repository
### Install Django dependencies
1. `cd` into the root directory
2. Run `pip install -r requirements.txt`
### Install React dependencies
1. `cd` into `frontend/` 
2. Run `npm install`

### Run Django tests
1. `cd` into the root directory
2. Run `python manage.py test`
### Run Jest + React tests
1. `cd` into `frontend/` 
2. Run `npm run test`
 
## Attributions
- Frontend structure based on <a href="https://github.com/duvainel/weather-app">weather app (MIT License)</a> by <a href="https://github.com/duvainel">@duvainel</a>
- Background image by <a href="https://pixabay.com/users/12019-12019/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=2184940">David Mark</a> from <a href="https://pixabay.com//?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=2184940">Pixabay</a>


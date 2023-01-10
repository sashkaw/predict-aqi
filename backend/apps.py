import os
import joblib
from django.apps import AppConfig
from django.conf import settings


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'
    # Load LSTM model and data scaler once when app starts up
    MODEL_FILE = os.path.join(settings.MODELS, "aqi_LSTM.joblib")
    SCALER_FILE = os.path.join(settings.MODELS, "aqi_scaler.joblib")
    model = joblib.load(MODEL_FILE)
    scaler = joblib.load(SCALER_FILE)

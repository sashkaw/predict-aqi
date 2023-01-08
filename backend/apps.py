import os
import joblib
from django.apps import AppConfig
from django.conf import settings


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'
    # Load ML model once when app starts up
    #TODO: update this with new model
    #MODEL_FILE = os.path.join(settings.MODELS, "aqi_LSTM.joblib")
    #model = joblib.load(MODEL_FILE)

import os
import joblib
from django.apps import AppConfig
from django.conf import settings

class TestModel():
    def __init__(self) -> None:
        super().__init__()
    def predict(self, X_scaled_reshaped, batch_size):
        return X_scaled_reshaped * 1.2

class TestScaler():
    def __init__(self) -> None:
        super().__init__()
    def transform(self, a):
        return a * 0.5
    def inverse_transform(self, a):
        return a / 0.5

class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'
    # Load LSTM model and data scaler once when app starts up
    #MODEL_FILE = os.path.join(settings.MODELS, "aqi_LSTM.joblib")
    #SCALER_FILE = os.path.join(settings.MODELS, "aqi_scaler.joblib")
    #model = joblib.load(MODEL_FILE)
    #scaler = joblib.load(SCALER_FILE)
    model = TestModel()
    scaler = TestScaler()

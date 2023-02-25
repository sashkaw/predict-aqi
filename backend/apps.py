import os
import joblib
from django.apps import AppConfig
from django.conf import settings
from google.cloud import storage
from tempfile import TemporaryFile

def fetch_bucket(client, name, file):
    '''
    Load joblib file from Google Cloud Storage

    Parameters:
    client --- storage.Client instance
    name --- name of the bucket as string
    file --- name of the joblib file in the bucket as string

    Returns:
    contents --- object loaded from bucket (eg model, scaler)
    '''
    bucket = client.get_bucket(name)
    #select bucket file
    blob = bucket.blob(file)
    with TemporaryFile() as temp_file:
        #download blob into temp file
        blob.download_to_file(temp_file)
        temp_file.seek(0)
        #load into joblib
        contents=joblib.load(temp_file)

        return contents

#class TestModel():
#    def __init__(self) -> None:
#        super().__init__()
#    def predict(self, X_scaled_reshaped, batch_size):
#        return X_scaled_reshaped * 1.2

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
    ##MODEL_FILE = os.path.join(settings.MODELS, "aqi_LSTM.joblib")
    #SCALER_FILE = os.path.join(settings.MODELS, "aqi_scaler.joblib")
    #model = joblib.load(MODEL_FILE)
    #scaler = joblib.load(SCALER_FILE)
    #model = TestModel()
    scaler = TestScaler()

    # Load ML model from storage bucket
    storage_client = storage.Client()
    model = fetch_bucket(storage_client, settings.LSTM_BUCKET, 'aqi_LSTM.joblib')

    


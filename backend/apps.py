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

class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'
    # Load ML model and scaler from storage bucket on app startup
    storage_client = storage.Client()
    model = fetch_bucket(storage_client, settings.LSTM_BUCKET, 'aqi_LSTM.joblib')
    scaler = fetch_bucket(storage_client, settings.SCALER_BUCKET, 'aqi_scaler.joblib')

    


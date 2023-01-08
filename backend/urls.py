from django.urls import path
from .views import *

urlpatterns = [
    path('', view=Prediction.as_view(), name='predict'),
]

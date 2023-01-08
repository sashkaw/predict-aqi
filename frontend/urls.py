from django.urls import path
from .views import *

urlpatterns = [
    path('', view=Dashboard, name='dashboard'),
]

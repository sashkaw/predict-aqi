from django.shortcuts import render

# Create your views here.

def Dashboard(request, *args, **kwargs):
    return render(request, 'frontend/index.html')


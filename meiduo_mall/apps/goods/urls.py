from .views import *
from django.urls import path

urlpatterns = [
    path('index/', IndexView.as_view()),
]
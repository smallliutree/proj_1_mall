from django.urls import path
from . import views

urlpatterns = [
    path('image_codes/<uuid:key>/', views.ImageCodeView.as_view()),
]
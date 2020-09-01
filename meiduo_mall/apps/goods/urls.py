from .views import *
from django.urls import path

urlpatterns = [
    path('index/', IndexView.as_view()),
    path('list/<int:category_id>/skus/', ListView.as_view()),

    path('detail/', DetailView.as_view()),
]
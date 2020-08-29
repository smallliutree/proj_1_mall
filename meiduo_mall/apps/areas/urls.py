from django.conf.urls import url

from apps.areas.views import AreasView, SubAreasView
from . import views
from django.urls import path

urlpatterns = [
    path('areas/', AreasView.as_view()),
    path('areas/<int:parent_id>', SubAreasView.as_view()),

]
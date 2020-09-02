from django.conf.urls import url
from apps.carts import views
from django.urls import path

urlpatterns = [
    path('carts/',views.CartsView.as_view()),
]
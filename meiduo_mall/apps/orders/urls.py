from django.urls import path

# from apps.orders.views import OrderSettlementView
from apps.orders import views

urlpatterns = [
    path('orders/settlement/', views.OrderSettlementView.as_view())
]
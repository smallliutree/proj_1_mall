from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from apps.meiduo_admin import views

from . import views

urlpatterns = [
    path('authorizations/', obtain_jwt_token),
    path('statistical/total_count/', views.UserTotalCountView.as_view()),
    path('statistical/day_increment/', views.UserDayCountView.as_view()),
    path('statistical/day_active/', views.UserActiveCountView.as_view()),
    path('statistical/day_orders/', views.UserOrderCountView.as_view()),
    path('statistical/month_increment/', views.UserMonthCountView.as_view()),
]

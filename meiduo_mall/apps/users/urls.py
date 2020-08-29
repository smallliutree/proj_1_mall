from django.urls import path
from . import views

urlpatterns = [
    # 判断用户名是否重复
    path('usernames/<username:username>/count/',views.UsernameCountView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('info/', views.UserInfoView.as_view()),
    path('/addresses/create/', views.CreateAddressView.as_view()),
    path('/addresses/', views.AddressView.as_view()),
]
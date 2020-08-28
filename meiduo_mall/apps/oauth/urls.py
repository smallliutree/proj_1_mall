from django.conf.urls import url
from django.urls import path
from . import views
urlpatterns = [
    path('qq/authorization/', views.QQLoginURLView.as_view()),
    path('oauth_callback/', views.QQAuthUserView.as_view()),
]
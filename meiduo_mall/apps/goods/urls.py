from .views import *
from django.urls import path

urlpatterns = [
    path('index/', IndexView.as_view()),
    path('list/<int:category_id>/skus/', ListView.as_view()),
    path('hot/<int:category_id>/', HotView.as_view()),

    path('search/', MySearchView()),
    path('detail/<int:sku_id>/', DetailView.as_view()),
    path('detail/visit/<int:cat_id>/', GoodsVisitView.as_view()),
]
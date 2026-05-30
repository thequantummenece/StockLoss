from django.urls import path
from . import views

urlpatterns = [
    path('', views.market_data_view, name='market_data'),
]

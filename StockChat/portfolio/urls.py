from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_view, name='portfolio'),
    path('delete/<int:pk>/', views.portfolio_delete, name='portfolio_delete'),
]

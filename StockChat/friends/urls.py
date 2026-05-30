from django.urls import path
from . import views

urlpatterns = [
    path('', views.friends_list, name='friends'),
    path('search/', views.search_users, name='search_users'),
    path('request/<int:user_id>/', views.send_request, name='send_request'),
    path('accept/<int:pk>/', views.accept_request, name='accept_request'),
    path('decline/<int:pk>/', views.decline_request, name='decline_request'),
    path('cancel/<int:pk>/', views.cancel_request, name='cancel_request'),
    path('unfriend/<int:user_id>/', views.unfriend, name='unfriend'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='chat'),
    path('<int:user_id>/', views.conversation, name='conversation'),
    path('<int:user_id>/send/', views.send_message, name='send_message'),
    path('<int:user_id>/poll/', views.poll_messages, name='poll_messages'),
    path('unread/', views.unread_count, name='unread_count'),
]

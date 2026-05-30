from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='communities'),
    path('new/', views.post_create, name='post_create'),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('<int:pk>/vote/', views.post_vote, name='post_vote'),
    path('<int:pk>/comment/', views.post_comment, name='post_comment'),
    path('<int:pk>/delete/', views.post_delete, name='post_delete'),
]

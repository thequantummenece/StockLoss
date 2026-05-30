from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('communities/', include('communities.urls')),
    path('market-data/', include('market_data.urls')),
    path('friends/', include('friends.urls')),
    path('chat/', include('chat.urls')),
]

from django.contrib import admin
from .models import Portfolio


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'stock_name', 'quantity', 'invested', 'added_at')
    search_fields = ('ticker', 'stock_name', 'user__username')
    list_filter = ('added_at', 'user')

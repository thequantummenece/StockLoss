from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def market_data_view(request):
    return render(request, "market_data/market_data.html")

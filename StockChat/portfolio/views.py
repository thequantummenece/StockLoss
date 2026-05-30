from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PortfolioAddForm
from .models import Portfolio


@login_required
def portfolio_view(request):
    if request.method == "POST":
        form = PortfolioAddForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data["ticker"]
            stock_name = form.cleaned_data["stock_name"]
            quantity = form.cleaned_data["quantity"]
            invested = form.cleaned_data["invested"]

            updated = Portfolio.objects.filter(
                user=request.user, ticker=ticker
            ).update(
                quantity=F("quantity") + quantity,
                invested=F("invested") + invested,
            )
            if updated:
                messages.success(request, f"{ticker} updated — added {quantity} more shares.")
            else:
                Portfolio.objects.create(
                    user=request.user,
                    ticker=ticker,
                    stock_name=stock_name,
                    quantity=quantity,
                    invested=invested,
                )
                messages.success(request, f"{ticker} added to your portfolio!")
        else:
            messages.warning(request, "Please enter valid data for all fields.")

        return redirect("portfolio")

    holdings = Portfolio.objects.filter(user=request.user).order_by("ticker")
    totals = holdings.aggregate(
        total_invested=Sum("invested"),
        total_shares=Sum("quantity"),
    )

    return render(request, "portfolio/portfolio.html", {
        "holdings": holdings,
        "total_invested": totals["total_invested"] or 0,
        "total_shares": totals["total_shares"] or 0,
    })


@login_required
@require_POST
def portfolio_delete(request, pk):
    holding = get_object_or_404(Portfolio, pk=pk, user=request.user)
    ticker = holding.ticker
    holding.delete()
    messages.success(request, f"{ticker} removed from portfolio.")
    return redirect("portfolio")

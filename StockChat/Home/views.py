from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ContactForm, PortfolioAddForm
from .models import Contact, Portfolio


def home(request):
    return render(request, "Home/home.html")


def about(request):
    return render(request, "Home/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your form has been sent!")
            return redirect("contact")
        else:
            messages.warning(request, "Please correct the errors below.")
    else:
        form = ContactForm()
    return render(request, "Home/contact.html", {"form": form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "Home/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            # Validate the next parameter to prevent open redirects
            next_url = request.POST.get("next", request.GET.get("next", ""))
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "Home/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required
def portfolio_view(request):
    if request.method == "POST":
        form = PortfolioAddForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data["ticker"]
            stock_name = form.cleaned_data["stock_name"]
            quantity = form.cleaned_data["quantity"]
            invested = form.cleaned_data["invested"]

            # Use F() to avoid race conditions on concurrent updates
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

    return render(request, "Home/portfolio.html", {
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

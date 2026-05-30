from decimal import Decimal

from django import forms


class PortfolioAddForm(forms.Form):
    ticker = forms.CharField(max_length=20)
    stock_name = forms.CharField(max_length=100)
    quantity = forms.IntegerField(min_value=1)
    invested = forms.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))

    def clean_ticker(self):
        return self.cleaned_data["ticker"].strip().upper()

    def clean_stock_name(self):
        return self.cleaned_data["stock_name"].strip()

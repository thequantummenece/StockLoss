from decimal import Decimal, InvalidOperation

from django import forms

from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "email", "phone", "content", "dob"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "dob": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) < 3:
            raise forms.ValidationError("Name must be at least 3 characters.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if len(phone) < 10:
            raise forms.ValidationError("Phone number must be at least 10 characters.")
        return phone

    def clean_content(self):
        content = self.cleaned_data["content"]
        if len(content) < 3:
            raise forms.ValidationError("Message must be at least 3 characters.")
        return content


class PortfolioAddForm(forms.Form):
    ticker = forms.CharField(max_length=20)
    stock_name = forms.CharField(max_length=100)
    quantity = forms.IntegerField(min_value=1)
    invested = forms.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))

    def clean_ticker(self):
        return self.cleaned_data["ticker"].strip().upper()

    def clean_stock_name(self):
        return self.cleaned_data["stock_name"].strip()

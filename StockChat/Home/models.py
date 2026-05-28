from django.db import models
from django.contrib.auth.models import User


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    ticker = models.CharField(max_length=20, default='UNKNOWN')
    stock_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    invested = models.DecimalField(max_digits=12, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "ticker"],
                name="unique_user_ticker",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.ticker} x{self.quantity}"

    @property
    def avg_price(self):
        if self.quantity > 0:
            return round(self.invested / self.quantity, 2)
        return 0


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    content = models.TextField()
    dob = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.email}"

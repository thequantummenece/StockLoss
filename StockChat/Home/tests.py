from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Contact, Portfolio


class HomeViewTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to StockChat")

    def test_about_page_renders(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About StockChat")


class ContactViewTests(TestCase):
    def test_contact_page_renders(self):
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)

    def test_contact_form_valid_submission(self):
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890",
            "content": "Hello, this is a test message.",
        }
        response = self.client.post(reverse("contact"), data)
        self.assertRedirects(response, reverse("contact"))
        self.assertEqual(Contact.objects.count(), 1)
        contact = Contact.objects.first()
        self.assertEqual(contact.name, "Test User")
        self.assertEqual(contact.email, "test@example.com")

    def test_contact_form_invalid_short_name(self):
        data = {
            "name": "AB",
            "email": "test@example.com",
            "phone": "1234567890",
            "content": "Hello, this is a test message.",
        }
        response = self.client.post(reverse("contact"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)

    def test_contact_form_invalid_short_phone(self):
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "123",
            "content": "Hello, this is a test message.",
        }
        response = self.client.post(reverse("contact"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)

    def test_contact_form_invalid_email(self):
        data = {
            "name": "Test User",
            "email": "not-an-email",
            "phone": "1234567890",
            "content": "Hello, this is a test.",
        }
        response = self.client.post(reverse("contact"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)


class SignupViewTests(TestCase):
    def test_signup_page_renders(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user_and_logs_in(self):
        data = {
            "username": "newuser",
            "password1": "T3stP@ssw0rd!",
            "password2": "T3stP@ssw0rd!",
        }
        response = self.client.post(reverse("signup"), data)
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        # Check user is logged in
        home_response = self.client.get(reverse("home"))
        self.assertContains(home_response, "newuser")

    def test_signup_redirects_authenticated_user(self):
        user = User.objects.create_user("existing", password="pass1234")
        self.client.force_login(user)
        response = self.client.get(reverse("signup"))
        self.assertRedirects(response, reverse("home"))


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="T3stP@ss!")

    def test_login_page_renders(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_valid_credentials(self):
        data = {"username": "testuser", "password": "T3stP@ss!"}
        response = self.client.post(reverse("login"), data)
        self.assertRedirects(response, reverse("home"))

    def test_login_invalid_credentials(self):
        data = {"username": "testuser", "password": "wrong"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 200)

    def test_login_redirects_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("home"))

    def test_login_rejects_open_redirect(self):
        data = {"username": "testuser", "password": "T3stP@ss!"}
        response = self.client.post(reverse("login") + "?next=https://evil.com", data)
        # Should redirect to home, not to evil.com
        self.assertRedirects(response, reverse("home"))

    def test_login_allows_safe_next(self):
        data = {
            "username": "testuser",
            "password": "T3stP@ss!",
            "next": reverse("portfolio"),
        }
        response = self.client.post(reverse("login"), data)
        self.assertRedirects(response, reverse("portfolio"))


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass1234")
        self.client.force_login(self.user)

    def test_logout_requires_post(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_post_works(self):
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        # Verify logged out
        portfolio_response = self.client.get(reverse("portfolio"))
        self.assertNotEqual(portfolio_response.status_code, 200)


class PortfolioViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("trader", password="pass1234")
        self.client.force_login(self.user)

    def test_portfolio_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("portfolio"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_portfolio_page_renders_empty(self):
        response = self.client.get(reverse("portfolio"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No holdings yet")

    def test_add_stock(self):
        data = {
            "ticker": "aapl",
            "stock_name": "Apple Inc.",
            "quantity": "10",
            "invested": "1500.00",
        }
        response = self.client.post(reverse("portfolio"), data)
        self.assertRedirects(response, reverse("portfolio"))
        self.assertEqual(Portfolio.objects.count(), 1)
        holding = Portfolio.objects.first()
        self.assertEqual(holding.ticker, "AAPL")  # uppercased
        self.assertEqual(holding.quantity, 10)
        self.assertEqual(holding.invested, Decimal("1500.00"))

    def test_add_to_existing_stock_uses_f_expression(self):
        Portfolio.objects.create(
            user=self.user, ticker="AAPL", stock_name="Apple Inc.",
            quantity=10, invested=Decimal("1500.00"),
        )
        data = {
            "ticker": "AAPL",
            "stock_name": "Apple Inc.",
            "quantity": "5",
            "invested": "750.00",
        }
        response = self.client.post(reverse("portfolio"), data)
        self.assertRedirects(response, reverse("portfolio"))
        holding = Portfolio.objects.get(ticker="AAPL", user=self.user)
        self.assertEqual(holding.quantity, 15)
        self.assertEqual(holding.invested, Decimal("2250.00"))

    def test_add_stock_invalid_data(self):
        data = {
            "ticker": "",
            "stock_name": "Apple",
            "quantity": "0",
            "invested": "100",
        }
        response = self.client.post(reverse("portfolio"), data)
        self.assertRedirects(response, reverse("portfolio"))
        self.assertEqual(Portfolio.objects.count(), 0)

    def test_portfolio_totals(self):
        Portfolio.objects.create(
            user=self.user, ticker="AAPL", stock_name="Apple",
            quantity=10, invested=Decimal("1500.00"),
        )
        Portfolio.objects.create(
            user=self.user, ticker="GOOG", stock_name="Google",
            quantity=5, invested=Decimal("2500.00"),
        )
        response = self.client.get(reverse("portfolio"))
        self.assertEqual(response.context["total_invested"], Decimal("4000.00"))
        self.assertEqual(response.context["total_shares"], 15)


class PortfolioDeleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("trader", password="pass1234")
        self.client.force_login(self.user)
        self.holding = Portfolio.objects.create(
            user=self.user, ticker="AAPL", stock_name="Apple",
            quantity=10, invested=Decimal("1500.00"),
        )

    def test_delete_requires_post(self):
        response = self.client.get(
            reverse("portfolio_delete", args=[self.holding.pk])
        )
        self.assertEqual(response.status_code, 405)

    def test_delete_own_holding(self):
        response = self.client.post(
            reverse("portfolio_delete", args=[self.holding.pk])
        )
        self.assertRedirects(response, reverse("portfolio"))
        self.assertEqual(Portfolio.objects.count(), 0)

    def test_cannot_delete_other_users_holding(self):
        other = User.objects.create_user("other", password="pass1234")
        holding = Portfolio.objects.create(
            user=other, ticker="GOOG", stock_name="Google",
            quantity=5, invested=Decimal("1000.00"),
        )
        response = self.client.post(
            reverse("portfolio_delete", args=[holding.pk])
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Portfolio.objects.filter(user=other).count(), 1)

    def test_delete_nonexistent_holding(self):
        response = self.client.post(
            reverse("portfolio_delete", args=[99999])
        )
        self.assertEqual(response.status_code, 404)


class PortfolioModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("trader", password="pass1234")

    def test_avg_price(self):
        p = Portfolio.objects.create(
            user=self.user, ticker="AAPL", stock_name="Apple",
            quantity=10, invested=Decimal("1500.00"),
        )
        self.assertEqual(p.avg_price, Decimal("150.00"))

    def test_avg_price_zero_quantity(self):
        p = Portfolio(
            user=self.user, ticker="AAPL", stock_name="Apple",
            quantity=0, invested=Decimal("0"),
        )
        self.assertEqual(p.avg_price, 0)

    def test_str(self):
        p = Portfolio.objects.create(
            user=self.user, ticker="AAPL", stock_name="Apple",
            quantity=10, invested=Decimal("1500.00"),
        )
        self.assertEqual(str(p), "trader — AAPL x10")

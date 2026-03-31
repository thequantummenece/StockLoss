from django.test import TestCase
from django.urls import reverse

# Create your tests here.

class HomeViewTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to StockChat")

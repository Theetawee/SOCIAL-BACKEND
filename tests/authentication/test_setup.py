from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class TestSetUp(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("login")

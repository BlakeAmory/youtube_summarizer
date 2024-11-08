from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class SummarizerViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_single_video_summary_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("single_video_summary"))
        self.assertEqual(response.status_code, 200)

    def test_search_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)

    def test_history_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("history"))
        self.assertEqual(response.status_code, 200)

    def test_user_profile_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("user_profile"))
        self.assertEqual(response.status_code, 200)

from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """Код 200 при запросе к страницам"""
        pages = ['about:author', 'about:tech']
        for page in pages:
            response = self.guest_client.get(reverse(page))
            self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """При запросе к страницам
        применяется соответствующий шаблон"""
        pages = {
            'about:author': 'author.html',
            'about:tech': 'tech.html'
        }
        for page, template in pages.items():
            response = self.guest_client.get(reverse(page))
            self.assertTemplateUsed(response, template)

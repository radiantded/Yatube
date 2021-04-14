from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, User


USERNAME = 'Zhorik666'
INDEX_URL = reverse('index')


class TestCache(TestCase):
    def test_cache(self):
        self.user = User.objects.create(username=USERNAME)
        authorized_client = Client()
        authorized_client.force_login(self.user)
        response = authorized_client.get(INDEX_URL)
        Post.objects.create(
            text='text',
            author=self.user,
        )
        response_2 = authorized_client.get(INDEX_URL)
        self.assertNotEqual(response, response_2)

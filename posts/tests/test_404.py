from django.test import Client, TestCase

from posts.models import User


USERNAME = 'Жмых'
NON_EXISTENT_URL = 'about/group/nonexurl'


class Test404(TestCase):
    def test_404(self):
        self.user = User.objects.create(username=USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.assertEqual(
            self.authorized_client.get(NON_EXISTENT_URL).status_code, 404)

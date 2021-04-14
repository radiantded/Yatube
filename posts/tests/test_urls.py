from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


USERNAME = 'Zhorik666'
USERNAME_2 = 'Рулон_Обоев'
NEW_POST_URL = reverse('new_post')
PROFILE_URL = reverse('profile', kwargs={'username': USERNAME})
LOGIN_URL = reverse('login')
INDEX_URL = reverse('index')
GROUP_SLUG = 'slug'
GROUP_POSTS_URL = reverse('group_posts', kwargs={'slug': GROUP_SLUG})
NEW_POST_REDIRECT_URL = f'{LOGIN_URL}?next={NEW_POST_URL}'


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_2 = User.objects.create_user(username=USERNAME_2)
        cls.group = Group.objects.create(
            title='Группа',
            description='Описание',
            slug=GROUP_SLUG
        )
        cls.post = Post.objects.create(
            text='text',
            author=cls.user,
            group=cls.group
        )
        cls.POST_URL = reverse(
            'post', kwargs={
                'username': cls.user.username,
                'post_id': cls.post.id
            }
        )
        cls.POST_EDIT_URL = reverse(
            'post_edit', kwargs={
                'username': cls.user.username,
                'post_id': cls.post.id
            }
        )
        cls.POST_EDIT_REDIRECT_URL = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_2)

    def test_pages_status_codes(self):
        """Ожидаемые коды при открытии страниц авторизованным
        и неавторизованным пользователем"""
        data = [
            [self.guest_client, NEW_POST_URL, 302],
            [self.guest_client, self.POST_EDIT_URL, 302],
            [self.authorized_client_2, self.POST_EDIT_URL, 302],
            [self.guest_client, GROUP_POSTS_URL, 200],
            [self.guest_client, INDEX_URL, 200],
            [self.guest_client, PROFILE_URL, 200],
            [self.guest_client, self.POST_URL, 200],
            [self.authorized_client, NEW_POST_URL, 200],
            [self.authorized_client, self.POST_EDIT_URL, 200]
        ]
        for client, url, code in data:
            with self.subTest(client=client, url=url):
                self.assertEqual(client.get(url).status_code, code)

    def test_correct_template(self):
        """Страницы формируются с правильным шаблоном"""
        templates_url_list = [
            ['index.html', INDEX_URL],
            ['group.html', GROUP_POSTS_URL],
            ['new.html', NEW_POST_URL],
            ['new.html', self.POST_EDIT_URL],
            ['profile.html', PROFILE_URL],
            ['post.html', self.POST_URL],
        ]
        for template, url in templates_url_list:
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url), template
                )

    def test_user_redirect(self):
        data = [
            [self.guest_client, NEW_POST_URL, NEW_POST_REDIRECT_URL],
            [self.guest_client,
             self.POST_EDIT_URL,
             self.POST_EDIT_REDIRECT_URL],
            [self.authorized_client_2, self.POST_EDIT_URL, self.POST_URL]
        ]
        for client, url, redirect_url in data:
            with self.subTest(redirect_url=redirect_url):
                self.assertRedirects(client.get(url), redirect_url)

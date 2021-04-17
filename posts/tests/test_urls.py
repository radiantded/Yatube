from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


USERNAME = 'Zhorik666'
USERNAME_2 = 'Рулон_Обоев'
NEW_POST_URL = reverse('new_post')
PROFILE_URL = reverse('profile', kwargs={'username': USERNAME})
LOGIN_URL = reverse('login')
INDEX_URL = reverse('index')
FOLLOW_INDEX_URL = reverse('follow_index')
FOLLOW_INDEX_REDIRECT_URL = f'{LOGIN_URL}?next={FOLLOW_INDEX_URL}'
FOLLOW_URL = reverse('profile_follow', args=[USERNAME])
FOLLOW_REDIRECT_URL = f'{LOGIN_URL}?next={FOLLOW_URL}'
UNFOLLOW_URL = reverse('profile_unfollow', args=[USERNAME])
UNFOLLOW_REDIRECT_URL = f'{LOGIN_URL}?next={UNFOLLOW_URL}'
GROUP_SLUG = 'slug'
GROUP_POSTS_URL = reverse('group_posts', kwargs={'slug': GROUP_SLUG})
NEW_POST_REDIRECT_URL = f'{LOGIN_URL}?next={NEW_POST_URL}'
NON_EXISTENT_URL = 'about/group/nonexurl'


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_2 = User.objects.create_user(username=USERNAME_2)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client_2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2.force_login(cls.user_2)
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
        cls.ADD_COMMENT_URL = reverse(
            'add_comment', args=[USERNAME, cls.post.id]
        )

    def test_pages_status_codes(self):
        """Ожидаемые коды при открытии страниц авторизованным
        и неавторизованным пользователем"""
        data = [
            [self.guest_client, NEW_POST_URL, 302],
            [self.guest_client, self.POST_EDIT_URL, 302],
            [self.guest_client, FOLLOW_INDEX_URL, 302],
            [self.guest_client, FOLLOW_URL, 302],
            [self.guest_client, UNFOLLOW_URL, 302],
            [self.guest_client, self.ADD_COMMENT_URL, 302],
            [self.authorized_client, self.ADD_COMMENT_URL, 302],
            [self.authorized_client_2, FOLLOW_URL, 302],
            [self.authorized_client_2, self.POST_EDIT_URL, 302],
            [self.guest_client, GROUP_POSTS_URL, 200],
            [self.guest_client, INDEX_URL, 200],
            [self.guest_client, PROFILE_URL, 200],
            [self.guest_client, self.POST_URL, 200],
            [self.authorized_client, NEW_POST_URL, 200],
            [self.authorized_client, self.POST_EDIT_URL, 200],
            [self.authorized_client, FOLLOW_INDEX_URL, 200],
            [self.authorized_client, NON_EXISTENT_URL, 404],
        ]
        for client, url, code in data:
            with self.subTest(client=client, url=url, code=code):
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
            ['follow.html', FOLLOW_INDEX_URL]
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
            [self.guest_client, FOLLOW_INDEX_URL, FOLLOW_INDEX_REDIRECT_URL],
            [self.guest_client, FOLLOW_URL, FOLLOW_REDIRECT_URL],
            [self.guest_client, UNFOLLOW_URL, UNFOLLOW_REDIRECT_URL],
            [self.authorized_client_2, FOLLOW_URL, PROFILE_URL],
            [self.authorized_client_2, UNFOLLOW_URL, PROFILE_URL],
        ]
        for client, url, redirect_url in data:
            with self.subTest(redirect_url=redirect_url):
                self.assertRedirects(client.get(url), redirect_url)

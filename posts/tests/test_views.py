from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User, Follow
from posts.settings import POSTS_PER_PAGE


USERNAME = 'Zhorik666'
USERNAME_2 = 'Sanya_Pudge'
USERNAME_3 = 'Borodavka'
NEW_POST_URL = reverse('new_post')
PROFILE_URL = reverse('profile', kwargs={'username': USERNAME})
PROFILE_FOLLOW_URL = reverse('profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('profile_unfollow', args=[USERNAME])
INDEX_URL = reverse('index')
GROUP_SLUG = 'slug'
GROUP_2_POSTS_SLUG = 'slug2'
GROUP_POSTS_URL = reverse('group_posts', kwargs={'slug': GROUP_SLUG})
GROUP_2_POSTS_URL = reverse('group_posts', kwargs={'slug': GROUP_2_POSTS_SLUG})


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.user_2 = User.objects.create(username=USERNAME_2)
        cls.user_3 = User.objects.create(username=USERNAME_3)
        cls.group = Group.objects.create(
            title='Группа',
            description='Описание',
            slug=GROUP_SLUG
        )
        cls.group_2 = Group.objects.create(
            title='Группа 2',
            description='Описание',
            slug=GROUP_2_POSTS_SLUG
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.POST_URL = reverse(
            'post', kwargs={
                'username': USERNAME,
                'post_id': cls.post.id
            }
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_2)

    def test_templates_expected_context(self):
        """Шаблоны страниц формируются с правильным контекстом"""
        templates_urls = [
            [GROUP_POSTS_URL, 'page'],
            [INDEX_URL, 'page'],
            [PROFILE_URL, 'page'],
            [self.POST_URL, 'post']
        ]
        for url, context in templates_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if context == 'page':
                    self.assertEqual(len(response.context['page']), 1)
                    post = response.context['page'][0]
                if context == 'post':
                    post = response.context['post']
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.id, self.post.id)

    def test_templates_expected_group_context(self):
        """Шаблон группы формируется с правильным контекстом group"""
        group = self.authorized_client.get(GROUP_POSTS_URL).context['group']
        self.assertEqual(
            group.id,
            self.group.id
        ),
        self.assertEqual(
            group.title,
            self.group.title
        )
        self.assertEqual(
            group.description,
            self.group.description
        )

    def test_new_post_not_at_target_location(self):
        """Пост не появляется не на странице своей группы"""
        self.assertNotIn(
            self.post,
            self.authorized_client.get(GROUP_2_POSTS_URL).context.get('page')
        )

    def test_paginator(self):
        """Количество элементов на странице отображается
        согласно настройкам пагинатора"""
        urls = [INDEX_URL, GROUP_POSTS_URL, PROFILE_URL]
        for post in range(POSTS_PER_PAGE):
            Post.objects.create(
                author=self.user,
                text='Текст',
                group=self.group
            )
        for url in urls:
            with self.subTest(url=url):
                self.assertLessEqual(
                    len(self.authorized_client.get(url).context['page']),
                    POSTS_PER_PAGE
                )

    def test_templates_expected_author_context(self):
        """Шаблон страницы профиля формируются с правильным контекстом"""
        self.assertEqual(
            self.guest_client.get(PROFILE_URL).context['author'].username,
            self.user.username
        )

    def test_auth_user_subscribe_unsubscribe(self):
        following_count = Follow.objects.filter(author=self.user,
                                                user=self.user_2).count()
        self.authorized_client_2.get(PROFILE_FOLLOW_URL)
        following_count_2 = Follow.objects.filter(author=self.user,
                                                  user=self.user_2).count()
        self.assertEqual(following_count + 1, following_count_2)
        self.authorized_client_2.get(PROFILE_UNFOLLOW_URL)
        following_count_3 = Follow.objects.filter(author=self.user,
                                                  user=self.user_2).count()
        self.assertEqual(following_count_2 - 1, following_count_3)

    def test_post(self):
        self.authorized_client_2.get(PROFILE_FOLLOW_URL)
        self.assertIn(
            self.post,
            Post.objects.filter(author__following__user=self.user_2)
        )
        self.assertNotIn(
            self.post,
            Post.objects.filter(author__following__user=self.user_3)
        )

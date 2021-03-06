from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User, Follow
from yatube.settings import POSTS_PER_PAGE


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
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client_2 = Client()
        cls.authorized_client_3 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2.force_login(cls.user_2)
        cls.authorized_client_3.force_login(cls.user_3)
        cls.authorized_client_2.get(PROFILE_FOLLOW_URL)
        cls.FOLLOW_INDEX_URL = reverse('follow_index')

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

    def test_templates_expected_context(self):
        """Шаблоны страниц формируются с правильным контекстом"""
        templates_urls = [
            [GROUP_POSTS_URL, 'page'],
            [INDEX_URL, 'page'],
            [PROFILE_URL, 'page'],
            [self.POST_URL, 'post'],
            [self.FOLLOW_INDEX_URL, 'page']
        ]
        for url, context in templates_urls:
            with self.subTest(url=url):
                response = self.authorized_client_2.get(url)
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
        """Шаблоны страниц формируются с правильным контекстом профиля"""
        urls = [PROFILE_URL, self.POST_URL]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).context['author'].username,
                    self.user.username
                )

    def test_auth_user_subscribe(self):
        following_count = Follow.objects.filter(author=self.user,
                                                user=self.user_3).exists()
        self.authorized_client_3.get(PROFILE_FOLLOW_URL)
        following_count_2 = Follow.objects.filter(author=self.user,
                                                  user=self.user_3).exists()
        self.assertNotEqual(following_count, following_count_2)

    def test_auth_user_unsubscribe(self):
        following_count = Follow.objects.filter(author=self.user,
                                                user=self.user_3).exists()
        self.authorized_client_3.get(PROFILE_UNFOLLOW_URL)
        following_count_3 = Follow.objects.filter(author=self.user,
                                                  user=self.user_3).exists()
        self.assertEqual(following_count, following_count_3)

    def test_cache(self):
        cache.clear()
        response = self.authorized_client.get(INDEX_URL).content
        Post.objects.create(
            text='text',
            author=self.user,
        )
        response_2 = self.authorized_client.get(INDEX_URL).content
        self.assertEqual(response, response_2)
        cache.clear()
        response_3 = self.authorized_client.get(INDEX_URL).content
        self.assertNotEqual(response, response_3)

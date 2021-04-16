import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User, Comment


USERNAME = 'Zhorik666'
USERNAME_2 = 'Рулон_Обоев'
NEW_POST_URL = reverse('new_post')
LOGIN_URL = reverse('login')
FOLLOW_INDEX_URL = reverse('follow_index')
FOLLOW_URL = reverse('profile_follow', args=[USERNAME])
PROFILE_FOLLOW_URL = reverse('profile_follow', args=[USERNAME])
NEW_POST_REDIRECT_URL = f'{LOGIN_URL}?next={NEW_POST_URL}'
INDEX_URL = reverse('index')
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostFormTests(TestCase):
    @classmethod
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.user_2 = User.objects.create_user(username=USERNAME_2)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client_2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2.force_login(cls.user_2)
        cls.authorized_client_2.get(PROFILE_FOLLOW_URL)

        cls.group = Group.objects.create(
            title='Группа',
            description='Описание',
            slug='slug'
        )
        cls.group_2 = Group.objects.create(
            title='Группа_2',
            description='Описание_2',
            slug='slug_2'
        )
        cls.post = Post.objects.create(
            text='text',
            author=cls.user,
            group=cls.group
        )
        cls.POST_URL = reverse('post', args=[cls.user, cls.post.id])
        cls.POST_EDIT_URL = reverse('post_edit', args=[USERNAME, cls.post.id])
        cls.POST_EDIT_REDIRECT_URL = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_new_post_in_db(self):
        """В базе данных создаётся новая запись"""
        posts_ids = {post.id for post in Post.objects.all()}
        form_data = {
            'text': 'Текст',
            'group': self.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        response_2 = self.guest_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_2, NEW_POST_REDIRECT_URL)
        self.assertRedirects(response, INDEX_URL)
        for post in range(len(response.context['page'])):
            if response.context['page'][post].id not in posts_ids:
                new_post = response.context['page'][post]
                self.assertIn(
                    new_post,
                    self.authorized_client_2.get(
                        FOLLOW_INDEX_URL
                    ).context['page']
                )
                self.assertNotIn(
                    new_post,
                    self.authorized_client.get(
                        FOLLOW_INDEX_URL
                    ).context['page']
                )
                self.assertEqual(new_post.text, form_data['text'])
                self.assertEqual(new_post.group.id, form_data['group'])
                self.assertEqual(new_post.author, self.user)

    def test_new_post_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(NEW_POST_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': self.group_2.id,
            'image': SMALL_GIF
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        response_2 = self.guest_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_URL)
        self.assertRedirects(response_2, self.POST_EDIT_REDIRECT_URL)
        posts_count_after_editing = Post.objects.count()
        self.assertEqual(
            posts_count, posts_count_after_editing
        )
        self.assertEqual(response.context['post'].author, self.user)
        self.assertEqual(response.context['post'].text, form_data['text'])
        self.assertEqual(response.context['post'].group.id, form_data['group'])

    def test_add_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий',
        }
        self.guest_client.post(
            self.POST_URL,
            data=form_data,
            follow=True
        )
        comment_count_2 = Comment.objects.count()
        self.assertEqual(comment_count, comment_count_2)

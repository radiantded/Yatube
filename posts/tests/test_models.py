from django.test import TestCase

from posts.models import Post, Group, User


USERNAME = 'Zhorik666'


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Группа',
            description='Описание',
            slug='slug'
        )
        cls.post = Post.objects.create(
            text='text',
            author=cls.user,
            group=cls.group
        )

    def test_text_help_text(self):
        """help_text поля text совпадает с ожидаемым"""
        expected = 'Введите текст'
        self.assertEqual(
            Post._meta.get_field('text').help_text, expected
        )

    def test_text_verbose_name(self):
        """verbose_name полей совпадают с ожидаемыми"""
        verbose_names = {
            'text': 'Текст',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name,
                    expected
                )

    def test_post_str(self):
        """__str__ post - это строчка с сожержимым post.text"""
        self.assertIn(self.post.text[:20], str(self.post))

    def test_group_str(self):
        """__str__ group - это строчка с сожержимым group.title"""
        self.assertIn(self.group.title, str(self.group))

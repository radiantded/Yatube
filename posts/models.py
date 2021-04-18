from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(max_length=200, verbose_name='Текст',
                            help_text='Введите текст')
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='posts')
    group = models.ForeignKey('Group', verbose_name='Группа',
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ('-pub_date',)

    def __str__(self):
        return (
            f'{self.author.username}, '
            f'{self.group}, '
            f'{self.text[:20]}, '
            f'{self.pub_date}'
        )


class Group(models.Model):
    title = models.CharField('Название группы', max_length=200)
    description = models.TextField('Описание')
    slug = models.SlugField('Уникальный ключ', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, verbose_name='Пост',
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, verbose_name='Автор комментария',
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(max_length=200, verbose_name='Текст комментария',
                            help_text='Введите текст')
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self):
        return (
            f'{self.author.username}, '
            f'{self.text[:20]}, '
            f'{self.created}'
        )


class Follow(models.Model):
    user = models.ForeignKey(User, verbose_name='Подписчик',
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='subscription')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            f'Автор {self.author.username}, '
            f'Подписчик {self.user.username}, '
        )

    class UniqueConstraint:
        fields = ['user', 'author']

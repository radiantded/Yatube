# Generated by Django 3.1.7 on 2021-03-31 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20210323_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Текст', max_length=200, verbose_name='Текст'),
        ),
    ]

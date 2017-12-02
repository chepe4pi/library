# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-02 12:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0002_auto_20171129_1657'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('rating', models.PositiveSmallIntegerField(choices=[(0, 'Ужасно'), (1, 'Плохо'), (2, 'Так себе'), (3, 'Хорошо'), (4, 'Отлично')], verbose_name='Оценка')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookratings', to='catalog.Book', verbose_name='Книга')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookratings', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WishlistedBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlistedbooks', to='catalog.Book', verbose_name='Книга')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlistedbooks', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='wishlistedbook',
            unique_together=set([('book', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='bookrating',
            unique_together=set([('book', 'user')]),
        ),
    ]
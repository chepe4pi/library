# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-03 13:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0003_auto_20171202_1243'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBookRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('type', models.PositiveSmallIntegerField(verbose_name='Тип отношения')),
                ('value', models.CharField(blank=True, max_length=255, null=True, verbose_name='Значение')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userbookrelations', to='catalog.Book', verbose_name='Книга')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userbookrelations', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='bookmark',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='bookmark',
            name='book',
        ),
        migrations.RemoveField(
            model_name='bookmark',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='bookrating',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='bookrating',
            name='book',
        ),
        migrations.RemoveField(
            model_name='bookrating',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='wishlistedbook',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='wishlistedbook',
            name='book',
        ),
        migrations.RemoveField(
            model_name='wishlistedbook',
            name='user',
        ),
        migrations.DeleteModel(
            name='Bookmark',
        ),
        migrations.DeleteModel(
            name='BookRating',
        ),
        migrations.DeleteModel(
            name='WishlistedBook',
        ),
        migrations.AlterUniqueTogether(
            name='userbookrelation',
            unique_together=set([('book', 'user', 'type')]),
        ),
    ]

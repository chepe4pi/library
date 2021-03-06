# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-11 18:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20171206_1702'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('discount', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Скидка в процентах')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'группа скидок',
                'verbose_name_plural': 'группы скидок',
            },
        ),
        migrations.AddField(
            model_name='book',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Скидка в процентах'),
        ),
        migrations.AddField(
            model_name='book',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='book',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='books', to='catalog.Category', verbose_name='Категории'),
        ),
        migrations.AddField(
            model_name='book',
            name='discount_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='books', to='catalog.DiscountGroup', verbose_name='Группа скидок'),
        ),
    ]

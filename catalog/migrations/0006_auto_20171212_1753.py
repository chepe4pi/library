# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-12 17:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_auto_20171212_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Скидка в процентах'),
        ),
        migrations.AlterField(
            model_name='book',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Итоговая цена'),
        ),
        migrations.AlterField(
            model_name='book',
            name='price_original',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Цена без учета скидки'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-11 18:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_auto_20171211_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Скидка в процентах'),
        ),
        migrations.AlterField(
            model_name='book',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Цена'),
        ),
    ]

# Generated by Django 2.2 on 2020-04-24 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StudentSupport', '0018_auto_20200420_2154'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='div',
            field=models.IntegerField(choices=[(1, 1), (2, 2)], default=1),
        ),
    ]

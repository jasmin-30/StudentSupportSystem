# Generated by Django 2.2 on 2020-03-24 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StudentSupport', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='expiry_date',
        ),
        migrations.RemoveField(
            model_name='news',
            name='start_date',
        ),
        migrations.AlterField(
            model_name='user',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]

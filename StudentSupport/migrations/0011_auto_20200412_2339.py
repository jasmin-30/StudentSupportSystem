# Generated by Django 2.2 on 2020-04-12 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StudentSupport', '0010_faculty_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjects',
            name='subject_code',
            field=models.CharField(max_length=10),
        ),
    ]
